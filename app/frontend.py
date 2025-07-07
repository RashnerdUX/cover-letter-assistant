from typing import Dict, List,Any
import requests
import dotenv
import os
import time

import gradio as gr

from schema import ChatRequest, ChatResponse, FileData
from utils import convert_to_filedata

dotenv.load_dotenv()


def get_backend_url():
    """Get the backend URL with fallback options"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8081")
    if not backend_url.startswith("http"):
        backend_url = f"http://{backend_url}"
    return backend_url.rstrip("/")


def wait_for_backend(max_retries=30, delay=2):
    """Wait for backend to be ready"""
    backend_url = get_backend_url()
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{backend_url}/docs", timeout=5)
            if response.status_code == 200:
                print(f"Backend is ready at {backend_url}")
                return True
        except requests.exceptions.RequestException:
            print(
                f"Attempt {attempt + 1}/{max_retries}: Backend not ready, waiting {delay}s..."
            )
            time.sleep(delay)

    print(f"Backend failed to start after {max_retries} attempts")
    return False

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

    backend_url = get_backend_url()

    try:
        response = requests.post(f"{backend_url}/chat",
                                 json=user_request.model_dump())
        response.raise_for_status()

        data = response.json()

        result = ChatResponse(**data)

        return result.response
    except requests.exceptions.RequestException as e:
        return [f"Error connecting to backend service: {str(e)}"]


if __name__ == "__main__":
    # Wait for backend to be ready
    print("Waiting for backend to be ready...")
    if not wait_for_backend():
        print("WARNING: Backend may not be ready. Continuing anyway...")

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

    # Get port from environment (Google Cloud Run uses PORT env var)
    port = int(os.getenv("PORT", 8080))

    app.launch(
        server_name="0.0.0.0",
        server_port=port,
    )