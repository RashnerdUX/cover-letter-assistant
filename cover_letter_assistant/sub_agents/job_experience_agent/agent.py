from google.adk.agents import LlmAgent
from . import prompt

experience_agent = LlmAgent(
    name = "JobExperienceAgent",
    model = "gemini-2.5-flash-preview-05-20",
    description = "Use this to determine how the user's current feats fit the job description",
    instruction = prompt.JOB_EXPERIENCE_PROMPT,
    output_key= "user_experience"
)