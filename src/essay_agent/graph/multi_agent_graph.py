from langgraph.graph import StateGraph, START
from langgraph.graph import MessagesState
from langgraph_supervisor import create_supervisor
from src.essay_agent.agents.work_agent import work_agent
from src.essay_agent.agents.review_agent import review_agent 
from src.essay_agent.llm.llm_proxy import setup_llm

def create_multi_agent_graph():
    """Create and return the compiled multi-agent graph"""
    supervisor_llm = setup_llm()
    
    supervisor = create_supervisor(
        agents=[work_agent, review_agent],
        model=supervisor_llm,
        prompt=(
            "You manage a work_agent and a review_agent . "
            "The work_agent can read PDFs and answer questions, or find news articles on given topics. "
            "The review_agent reviews and critiques the generated content. "
            "Assign work to them based on the user's request."
        )
    ).compile()
    
    multi_agent_graph = (
        StateGraph(MessagesState)
        .add_node("supervisor", supervisor)
        .add_node("work_agent", work_agent)
        .add_node("review_agent", review_agent)
        .add_edge(START, "supervisor")
        .compile()
    )
    
    return multi_agent_graph
