from langgraph.prebuilt import create_react_agent
from src.essay_agent.llm.llm_proxy import setup_llm
from src.essay_agent.tools.document_tools import summarize_document
from src.essay_agent.tools.news_tools import get_related_news
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import MessagesState
from langgraph.types import Command
# from google.ai.generativelanguage_v1beta.types import Tool as GenAITool


# Setup your LLM client
llm = setup_llm()

# Define tool wrappers for agent compatibility
# def summarize_document_tool(file_path: str, prompt: str = None) -> str:
#     """Summarize a document given a file path and optional prompt."""
#     try:
#         return summarize_document(file_path, prompt)
#     except FileNotFoundError:
#         return f"Error: The file '{file_path}' was not found. Please check the path."

# def get_related_news_tool(topic: str) -> str:
#     """Get related news for a topic."""
#     news = get_related_news(topic)
#     return str(news)
from langchain_core.tools import tool

@tool
def summarize_document_tool(file_path: str, prompt: str = None) -> str:
    """Summarize a document given a file path and optional prompt."""
    try:
        return summarize_document(file_path, prompt)
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found. Please check the path."

@tool
def get_related_news_tool(topic: str) -> str:
    """Get related news for a topic."""
    news = get_related_news(topic)
    return str(news)


# Create the agent
# Update your work agent's prompt to handle JSON data properly
def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Transfer to {agent_name}"

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState], 
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(  
            goto=agent_name,  
            update={"messages": state["messages"] + [tool_message]},  
            graph=Command.PARENT,  
        )
    return handoff_tool
transfer_to_review = create_handoff_tool(agent_name="review_agent", description="Transfer to review agent for content review")
   

work_agent = create_react_agent(
    model=llm,
    tools=[summarize_document_tool, get_related_news_tool,transfer_to_review],
    # tools=[summarize_document_tool, GenAITool(google_search = {}), transfer_to_review],
    name="work_agent",
    prompt=(
        "You are a helpful assistant. "
        "u take document and give to summarize_document_tool  and answer the questions related to document"
        "For news requests, use get_related_news_tool and then process the returned data. "
        "Always present the results in a clear, organized format with titles, summaries, and sources. "
        "If the user asks for top 5 articles, select the 5 most relevant ones."
    )
)
# print(get_related_news_tool("India"))
# print(summarize_document_tool("/Users/a0k0hnf/Documents/tp.pdf", "Summarize the document."))
# print(work_agent.invoke({"messages": [{"role": "user", "content": "summarize the document at /Users/a0k0hnf/Documents/tp.pdf"}]}))








