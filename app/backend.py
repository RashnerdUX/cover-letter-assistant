import asyncio

import uvicorn
from fastapi import FastAPI, Depends, Body
from contextlib import asynccontextmanager
from types import SimpleNamespace
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events import Event
from dotenv import load_dotenv
from typing import AsyncIterator

from cover_letter_assistant.agent import root_agent as cover_letter_agent
from schema import ChatRequest, ChatResponse
from utils import format_for_adk

#Load our environment variables
load_dotenv()

#Global variables
APP_NAME = "cover_letter_assistant"
USER_ID = ""
SESSION_ID = ""

# Application state to hold service contexts
#This is simply holding the value of this important services for the adk
class AppContexts(SimpleNamespace):
    """A class to hold application contexts with attribute access"""

    session_service: InMemorySessionService = None
    artifact_service: InMemoryArtifactService = None
    agent_runner: Runner = None

# Initialize application state
#The app_contexts object stores the runner, service and artifact objects
app_contexts = AppContexts()

#This helps to define logic that should be executed before the server is
# officially started
@asynccontextmanager
async def lifespan(FastAPI):
    #This loads when the app starts
    app_contexts.session_service = InMemorySessionService()
    app_contexts.artifact_service = InMemoryArtifactService()
    app_contexts.agent_runner = Runner(
        app_name=APP_NAME,
        agent= cover_letter_agent,
        session_service=app_contexts.session_service,
        artifact_service=app_contexts.artifact_service,
    )
    yield
    #This loads after the app closes

# Helper function to get application state as a dependency
async def get_app_contexts() -> AppContexts:
    return app_contexts

app = FastAPI(title="Cover Letter Assistant API", lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
async def chat(
        request: ChatRequest = Body(...),
        app_context: AppContexts = Depends(get_app_contexts)
) -> ChatResponse:
    print(request)
    #Set the user and session id
    user_id = USER_ID or "default_user" #TODO: Create a user class and use ID
    # here
    session_id = SESSION_ID or "default_session" #TODO: Create a better session

    #Set the final response and possible errors
    final_response_text = "The Agent was unable to process your request"

    #Prepare the user message in ADK format
    content = await asyncio.to_thread(
        format_for_adk,
        request=request,
        user_id=user_id,
        session_id=session_id,
        app_name=APP_NAME,
        artifact_service=app_context.artifact_service,
    )

    #Check for a session and initialize chat session
    if not await app_context.session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    ):
        await app_context.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

    try:
        #Get the stream of events from the agent
        events_stream: AsyncIterator[Event]= app_context.agent_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message= content,
        )

        #Check through the stream
        async for event in events_stream:
            if event.is_final_response():
                #This checks for the final output after the agent runs
                if event.content and event.content.parts:
                    #Check if the event returned content
                    #Set the final response text to the final output from the
                    # agent
                    final_response_text = event.content.parts[0].text
                elif event.partial:
                    final_response_text = (
                        "Agent is still processing request. No result ready"
                    )
                    continue
                break

        return ChatResponse(response=final_response_text,)

    except Exception as e:
        return ChatResponse(
            response="", error=f"An error occurred. This is it {e}",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)




