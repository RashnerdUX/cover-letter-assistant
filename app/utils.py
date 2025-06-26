import os
import base64
from typing import List
import mimetypes

from google.adk.artifacts import InMemoryArtifactService
from google.genai.types import Part, Content

from schema import FileData, ChatRequest


def load_instruction_from_file(file:str, default_instruction:str = "Do nothing"):
    """
    This function takes a file_path and tries to read the text within it.
    If the file doesn't exist, default instruction is used instead.

    :param file:
    :param default_instruction:
    :return: Instructions present in the file
    """
    instruction = default_instruction

    try:
        file_path = os.path.join(os.path.dirname(__file__), file)
        with open(file_path) as f:
            instruction = f.read()
            print(f"Successfully read the file - {file}")
    except FileNotFoundError:
        print(f"{file} couldn't be found")
    except Exception as e:
        print(f"Error reading {file}: {e}")
    return instruction

def get_file_name(user_id):
    """
    This simply returns a standardized name for the pdf being uploaded by the user
    :param user_id:
    :return:
    """
    return f"CV for {user_id}"

def convert_to_filedata(file:str) ->FileData:
    """

    :param file:
    :return:
    """
    with open(file, "rb") as f:
        file_bytes = f.read()
    encoded = base64.b64encode(file_bytes).decode("utf-8")

    file_data = FileData(
        serialized_file=encoded,
        mime_type= mimetypes.guess_type(file)[0],
    )
    return file_data

def store_file(
    file: FileData,
    artifact_service: InMemoryArtifactService,
    user_id:str,
    session_id:str,
    app_name:str,
    ):
    """

    :param file:
    :param artifact_service:
    :param user_id:
    :param session_id:
    :param app_name:
    :return:
    """

    #Initialize Artifact service
    memory = artifact_service

    #Check if file already exists
    existing_artifacts = memory.list_versions(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=get_file_name(user_id=user_id),
    )
    #If a version of the artifact exists then just break
    if existing_artifacts:
        return

    #Create the artifact
    mime_type = "application/pdf"
    artifact = Part.from_bytes(
        mime_type=mime_type,
        data= base64.b64decode(file.serialized_file),
    )

    #Save the artifact
    memory.save_artifact(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=get_file_name(user_id=user_id),
        artifact=artifact,
    )

def format_for_adk(request: ChatRequest, user_id:str,
                   session_id:str, app_name:str, artifact_service) -> (
        Content):
    """
    :param artifact_service:
    :param app_name:
    :param session_id:
    :param request:
    :param user_id:
    :return: Content
    """

    #Create the parts before file is processed
    parts: List[Part] = []
    #First I need to save the files that the user passes
    if request.file:
        store_file(
            file=request.file,
            user_id=user_id,
            session_id=session_id,
            app_name=app_name,
            artifact_service=artifact_service,
        )
        parts.append(Part.from_bytes(
            data=base64.b64decode(request.file.serialized_file),
            mime_type=request.file.mime_type
        ))
    #Next I need to add messages
    parts.append(Part(text=request.message))

    #Return the content
    return Content(role="user", parts=parts)


