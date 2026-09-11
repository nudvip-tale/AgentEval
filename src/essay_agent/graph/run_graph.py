from src.essay_agent.graph.multi_agent_graph import create_multi_agent_graph
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage


def run_multi_agent_workflow_silent(user_message: str):
    """Run the workflow and return results without printing"""
    graph = create_multi_agent_graph()
    results = []
    
    
    
    for chunk in graph.stream({
        "messages": [
            HumanMessage(content=user_message)  
        ]
    },subgraphs=True):
        results.append(chunk)
    #   print(results)
    #   print("\n")
   
   

    return results

