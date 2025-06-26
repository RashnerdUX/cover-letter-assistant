from google.adk.agents import LlmAgent

from . import prompt

proposal_writing_agent = LlmAgent(
    name = "ProposalWritingAgent",
    model = "gemini-2.5-flash-preview-05-20",
    description="Use this to combine what the user has done to what the job expects the user to do",
    instruction = prompt.PROPOSAL_WRITING_PROMPT,
    output_key="Proposal Letter",
)