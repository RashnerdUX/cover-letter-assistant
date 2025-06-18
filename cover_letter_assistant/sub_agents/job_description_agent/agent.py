from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from . import prompt

job_description_agent = LlmAgent(
    name = "JobDescriptionAgent",
    model = "gemini-2.5-flash-preview-05-20",
    description = "Use this to understand what the job expects from the user",
    instruction = prompt.JOB_DESCRIPTION_PROMPT,
    output_key="job_requirements",
    tools = [google_search]
)