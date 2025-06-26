from typing import Dict, List,Any
import requests

import gradio as gr

from schema import ChatRequest, ChatResponse, FileData
from utils import convert_to_filedata


def connect_to_backend(
    message: Dict[str, Any],
    history: List[Dict[str, Any]],
):
    #Get file if needed
    file = None
    if isinstance(message, dict):
        if uploaded_file := message.get("files", []):
            file = convert_to_filedata(uploaded_file[0])

    #The request
    user_request = ChatRequest(
        message= message.get("text", "") if isinstance(message, dict) else
    message,
        session_id="default_session",
        user_id="default_user",
        file= file if isinstance(file, FileData) else None,
    )

    try:
        response = requests.post("http://127.0.0.1:8081/chat",
                                 json=user_request.model_dump())
        response.raise_for_status()

        data = response.json()

        result = ChatResponse(**data)

        return result.response
    except requests.exceptions.RequestException as e:
        return [f"Error connecting to backend service: {str(e)}"]


if __name__ == "__main__":
    app = gr.ChatInterface(
        fn= connect_to_backend,
        title= "Cover Letter Assistant",
        description="This is an agent specifically designed to construct a "
                    "cover letter that captures your best skills and "
                    "personality in less than 5 minutes",
        type="messages",
        multimodal=True,
        textbox= gr.MultimodalTextbox(file_types=["file"], interactive=True)
    )

    app.launch(
        server_name="127.0.0.1",
        server_port=8080,
    )