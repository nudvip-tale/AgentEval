from langgraph.prebuilt import create_react_agent
from src.essay_agent.llm.llm_proxy import setup_llm
from src.essay_agent.tools.critic_tools import critic_review

# Setup a dedicated LLM client for the ReviewAgent
review_llm = setup_llm()

from langchain_core.tools import tool

# Define the review tool wrapper for agent compatibility
@tool
def review_tool(content: str) -> str:
    """ReviewAgent reviews content and provides feedback."""
    return critic_review(content)

# Create the ReviewAgent as a ReAct agent
review_agent = create_react_agent(
    model=review_llm,
    tools=[review_tool],
    name="review_agent",
    prompt=(
        "You are a critical review agent. Your job is to analyze content and provide specific, detailed feedback. "
        "When reviewing content, you must use the review_tool to analyze it thoroughly. "
        "Provide constructive criticism on relevance, completeness, accuracy, quality, and specific issues. "
        "Be critical and specific - do not just say 'looks good' or give generic responses. "
        "Always use the review_tool to perform your analysis."
    )
)