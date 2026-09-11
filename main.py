import ssl
import sys

# Patch SSL context to ignore corrupted Windows store certificates
try:
    _orig_load_windows_store_certs = ssl.SSLContext._load_windows_store_certs
    def _safe_load_windows_store_certs(self, storename, purpose):
        try:
            _orig_load_windows_store_certs(self, storename, purpose)
        except ssl.SSLError:
            pass  # Ignore corrupted certs
    ssl.SSLContext._load_windows_store_certs = _safe_load_windows_store_certs
except AttributeError:
    pass

# Automatically load .env from the project root directory
import os
try:
    project_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(project_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()
except Exception:
    pass

from langgraph.graph import StateGraph, END, START
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage,convert_to_openai_messages
from src.essay_agent.agents.work_agent import work_agent,summarize_document_tool
from src.essay_agent.agents.review_agent import review_agent 
from src.essay_agent.llm.llm_proxy import setup_llm
from src.essay_agent.configs.app_config import settings
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import MessagesState
from langgraph.types import Command
from src.essay_agent.graph.multi_agent_graph import create_multi_agent_graph
from src.essay_agent.graph.run_graph import run_multi_agent_workflow_silent
from langgraph_supervisor import create_supervisor
import json
from src.essay_agent.graph.evaluation import evaluate_tool_usage
from src.essay_agent.ai_eval._intent_resolution import IntentResolutionEvaluator
from src.essay_agent.graph.evaluation import run_trajectory_evaluations
import time



# def main():
#     """Main entry point"""
#     user_message = "find 5 related news articles on trump , then review the summary for accuracy and coherence."
    
#     response = run_multi_agent_workflow_silent(user_message)
#     print(f"Response type: {type(response)}")
#     print("\n=== EVALUATION RESULT ===")
#     print('\n')
#     tool_calls = evaluate_tool_usage(user_message)
#     print("\n=== INTENT RESOLUTION EVALUATION ===")
#     # print('\n')
#     # print(response)
#     print("\n=== Trajectory  ===")
#     print(tool_calls)
#     print('\n')
#     evaluator = IntentResolutionEvaluator(threshold=3)
    
#     # Ensure response is a string for evaluation
#     response_str = str(response) if response else "No response generated"
    
#     intent_result = evaluator(
#         query=user_message,
#         response=response_str,
#         tool_calls=tool_calls,  
#         #  tool_definitions=tool_definitions  
#     )
    
#     # Access the results using the correct keys
#     score = intent_result.get('intent_resolution', 0)
#     explanation = intent_result.get('intent_resolution_reason', 'No explanation provided')
#     result = intent_result.get('intent_resolution_result', 'unknown')
    
#     print(f"Intent Resolution Score: {score}/5")
#     print(f"Result: {result}")
#     print(f"Explanation: {explanation}")
        
# if __name__ == "__main__":
#         main()

from langgraph.graph import StateGraph, END, START
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, convert_to_openai_messages
from src.essay_agent.agents.work_agent import work_agent, summarize_document_tool
from src.essay_agent.agents.review_agent import review_agent 
from src.essay_agent.llm.llm_proxy import setup_llm
from src.essay_agent.configs.app_config import settings
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import MessagesState
from langgraph.types import Command
from src.essay_agent.graph.multi_agent_graph import create_multi_agent_graph
from src.essay_agent.graph.run_graph import run_multi_agent_workflow_silent
from langgraph_supervisor import create_supervisor
import json
from src.essay_agent.graph.evaluation import evaluate_tool_usage, evaluate_multiple_prompts
from src.essay_agent.ai_eval._intent_resolution import IntentResolutionEvaluator

# import os
# import certifi

# os.environ["SSL_CERT_FILE"] = certifi.where()
# os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

def evaluate_intent_resolution(user_message: str, response, tool_calls):
    """Evaluate intent resolution for a single prompt"""
    evaluator = IntentResolutionEvaluator(threshold=3)
    
    # Ensure response is a string for evaluation
    
    response_str = str(response) if response else "No response generated"
    # print("response generated:\n\n")
    # print('\n')
    # print(response_str.AIMessage.content if isinstance(response_str, AIMessage) else response_str)
    intent_result = evaluator(
        query=user_message,
        response=response_str,
        tool_calls=tool_calls,  
    )
    
    # Access the results using the correct keys
    score = intent_result.get('intent_resolution', 0)
    explanation = intent_result.get('intent_resolution_reason', 'No explanation provided')
    result = intent_result.get('intent_resolution_result', 'unknown')
    
    return {
        'score': score,
        'explanation': explanation,
        'result': result
    }

def evaluate_single_prompt(user_message: str):
    """Evaluate a single prompt with both trajectory and intent resolution"""
    print(f"\n{'='*80}")
    print(f"EVALUATING PROMPT: {user_message}")
    print(f"{'='*80}")
    
    try:
        # Run the workflow
        response = run_multi_agent_workflow_silent(user_message)
        # print(f"Response type: {type(response)}")
        
        # Evaluate tool usage and trajectory
        tool_calls, trajectory_results = evaluate_tool_usage(user_message)
        
        # Evaluate intent resolution
        print("\n=== INTENT RESOLUTION EVALUATION ===")
        intent_results = evaluate_intent_resolution(user_message, response, tool_calls)
        
        print(f"Intent Resolution Score: {intent_results['score']}/5")
        print(f"Result: {intent_results['result']}")
        print(f"Explanation: {intent_results['explanation']}")
        
        return {
            'trajectory_results': trajectory_results,
            'intent_results': intent_results,
            'response': response,
            'tool_calls': tool_calls
        }
        
    except Exception as e:
        print(f"Error evaluating prompt: {e}")
        return {'error': str(e)}

def evaluate_all_prompts():
    """Evaluate all test prompts"""
    # Define test prompts
    test_prompts = [
        "Tell me about black holes in short.",
    ]
    
    # Store all results
    all_results = {}
    
    for i, user_message in enumerate(test_prompts, 1):
        print(f"\n{'='*120}")
        print(f"EVALUATING PROMPT {i}: {user_message}")
        print(f"{'='*120}")
        
        try:
            # Run the workflow
            response = run_multi_agent_workflow_silent(user_message)
            # print(f"Response type: {type(response)}")
            
            # Evaluate tool usage and trajectory
            tool_calls, trajectory_results = evaluate_tool_usage(user_message)
            
            # Evaluate intent resolution
            print("\n=== INTENT RESOLUTION EVALUATION ===")
            intent_results = evaluate_intent_resolution(user_message, response, tool_calls)
            
            print(f"Intent Resolution Score: {intent_results['score']}/5")
            print(f"Result: {intent_results['result']}")
            print(f"Explanation: {intent_results['explanation']}")
            
            # Store results
            all_results[user_message] = {
                'trajectory_results': trajectory_results,
                'intent_results': intent_results,
                'response': response,
                'tool_calls': tool_calls
            }
            
        except Exception as e:
            print(f"Error evaluating prompt {i}: {e}")
            all_results[user_message] = {'error': str(e)}
            print(e)
        time.sleep(5)
        
    
    # Print summary
    print_evaluation_summary(all_results)
    
    return all_results

def print_evaluation_summary(all_results):
    """Print a summary of all evaluation results"""
    print(f"\n{'='*80}")
    print("EVALUATION SUMMARY")
    print(f"{'='*80}")
    
    for i, (prompt, results) in enumerate(all_results.items(), 1):
        print(f"\nPrompt {i}: {prompt[:50]}...")
        if 'error' in results:
            print(f"  ERROR: {results['error']}")
        else:
            intent_score = results.get('intent_results', {}).get('score', 0)
            print(f"  Intent Resolution Score: {intent_score}/5")
            
            # Summary of trajectory results
            trajectory_results = results.get('trajectory_results', {})
            for eval_type, result in trajectory_results.items():
                if result and isinstance(result, dict):
                    # Fixed: use 'score' instead of 'trajectory_match'
                    score = result.get('score', 0)
                    # Convert boolean to 1/0 for display, or use the actual score value
                    display_score = 1 if score is True else (0 if score is False else score)
                    print(f"  {eval_type.title()} Trajectory Match: {display_score}")

def main():
    """Main entry point"""
    all_results = evaluate_all_prompts()
if __name__ == "__main__":
    main()   
    


# def main():
#     # user_msg=input("Enter your message: ")
#     response = run_multi_agent_workflow_silent("take this document /Users/a0k0hnf/Documents/tp.pdf and give summary, review the generated content")
#     print("\n\n Response Generated\n\n")
#     print(response.AIMessage.content if isinstance(response, AIMessage) else response)
# if __name__ == "__main__":
#     main()
