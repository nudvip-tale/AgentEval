import pytest
from src.essay_agent.graph.evaluation import evaluate_tool_usage
from main import evaluate_intent_resolution
from src.essay_agent.graph.run_graph import run_multi_agent_workflow_silent


class TestEvaluateIntentResolutionWithTrajectory:
    
    def test_evaluate_intent_resolution_real_workflow_execution(self):
        """Test intent resolution with actual workflow execution"""
        user_message = "find 5 related news articles on trump , then review the summary for accuracy and coherence."
        
        # Get actual tool calls from workflow
        tool_calls, _ = evaluate_tool_usage(user_message)
        
        # Run actual workflow to get real response
        response = run_multi_agent_workflow_silent(user_message)
        
        # Evaluate intent resolution with real data (no mocking)
        result = evaluate_intent_resolution(user_message, response, tool_calls)
        
        # Verify the score meets quality threshold for multi-step task
        assert result['score'] >= 4, f"Expected score >= 4 for complex multi-step task, got {result['score']}"
        assert result['result'] in ['pass', 'good', 'excellent'], f"Expected pass/good/excellent result, got {result['result']}"
        assert len(result['explanation']) > 0, "Explanation should not be empty"
        
        # Print actual results for verification
        print(f"Intent Resolution Score: {result['score']}")
        print(f"Result Classification: {result['result']}")
        print(f"Explanation: {result['explanation']}")

    def test_evaluate_intent_resolution_walmart_workflow(self):
        """Test with Walmart news search - real execution"""
        user_message = "find 5 related news articles on walmart"
        
        # Get real data from workflow
        tool_calls, _ = evaluate_tool_usage(user_message)
        response = run_multi_agent_workflow_silent(user_message)
        
        # Evaluate with real data
        result = evaluate_intent_resolution(user_message, response, tool_calls)
        
        assert result['score'] >= 3, f"Expected score >= 3, got {result['score']}"
        assert 'score' in result
        assert 'result' in result
        assert 'explanation' in result
        
        print(f"Walmart Score: {result['score']}, Result: {result['result']}")

