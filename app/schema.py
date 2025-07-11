from pydantic import BaseModel
from typing import List, Optional

class FileData(BaseModel):
    """
    Model for the CV/Resume file that the user will upload

    Attributes
        serialized_file: The bytes form of the file uploaded by user
    """
    serialized_file: str
    mime_type: str

class ChatRequest(BaseModel):
    """
    Model for each chat message that the user will provide for the agent

    Attributes
        message: The responses from the user
        file: The user's CV
        session_id: The identifier for the session
        user_id: The identifier for the user
    """
    message:str
    file: Optional[FileData] = None
    session_id: str = "default_session"
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    """
    Model for the ChatResponse provided by the Agent

    Attributes
        response: The agent's final response to the user
        thinking_process: The agent's thought process which is optional
        unless requested for
        attachments: Any files generated by the agent for the user
        error: Error messages if agent encounters a problem
    """
    response: str
    thinking_process: Optional[str] = None
    attachments: Optional[List[FileData]] = None
    error: Optional[str] = None
