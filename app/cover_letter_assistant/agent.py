from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService

from . import prompt
from .sub_agents.job_description_agent import job_description_agent
from .sub_agents.job_experience_agent import experience_agent
from .sub_agents.letter_writing_agent import proposal_writing_agent


"""
Notes
It's possible to create a custom tool - function, class, module or package 
and load in the tools attributes of the agent
"""


cover_letter_assistant = LlmAgent(
    name = "CoverLetterAI",
    model = "gemini-2.5-flash",
    description = "You help users create beautiful personalised cover letters for job applications",
    instruction = prompt.COVER_LETTER_PROMPT,
    output_key = "cover_letter",
    tools = [
        AgentTool(agent=job_description_agent),
        AgentTool(agent=experience_agent),
        AgentTool(agent=proposal_writing_agent),
    ],
)

root_agent = cover_letter_assistant

artifact_service = InMemoryArtifactService()
session_service = InMemorySessionService()

runner = Runner(
    agent=cover_letter_assistant,
    app_name="Cover Letter Assistant",
    artifact_service= artifact_service,
    session_service= session_service,
)