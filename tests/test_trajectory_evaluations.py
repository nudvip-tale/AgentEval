# import pytest
# import json
# from unittest.mock import Mock, patch, MagicMock
# from src.essay_agent.graph.evaluation import evaluate_tool_usage, run_trajectory_evaluations


# class TestTrajectoryEvaluations:
#     """Test cases for trajectory evaluation functions using actual trajectory data"""
    
#     @pytest.fixture(scope="class")
#     def actual_outputs_cache(self):
#         """Cache actual outputs to avoid multiple workflow runs"""
#         cache = {}
        
#         def get_outputs(user_message):
#             if user_message not in cache:
#                 outputs, _ = evaluate_tool_usage(user_message)
#                 cache[user_message] = outputs
#             return cache[user_message]
        
#         return get_outputs

#     @pytest.fixture
#     def sample_user_messages(self):
#         """Sample user messages for testing"""
#         return [
#             "find 5 related news articles on trump , then review the summary for accuracy and coherence.",
#             "find 5 related news articles on walmart"
#         ]

#     @patch('src.essay_agent.graph.evaluation.create_trajectory_match_evaluator')
#     def test_run_trajectory_evaluations_all_modes(self, mock_create_evaluator, actual_outputs_cache, sample_user_messages):
#         """Test that all evaluation modes are executed with actual trajectory data"""
#         user_message = sample_user_messages[0]  # Use first message
#         actual_outputs = actual_outputs_cache(user_message)
#         reference_outputs = actual_outputs  # Use same as reference for testing
        
#         # Mock evaluator results
#         evaluation_results = {
#             'unordered': {'score': True, 'reasoning': 'Unordered match successful'},
#             'subset': {'score': True, 'reasoning': 'Subset match successful'},
#             'superset': {'score': False, 'reasoning': 'Not a superset'},
#             'unordered_with_overrides': {'score': True, 'reasoning': 'Match with overrides'}
#         }
        
#         def create_mock_evaluator(*args, **kwargs):
#             mock_eval = Mock()
#             if 'tool_args_match_overrides' in kwargs:
#                 mock_eval.return_value = evaluation_results['unordered_with_overrides']
#             elif kwargs.get('trajectory_match_mode') == 'unordered':
#                 mock_eval.return_value = evaluation_results['unordered']
#             elif kwargs.get('trajectory_match_mode') == 'subset':
#                 mock_eval.return_value = evaluation_results['subset']
#             elif kwargs.get('trajectory_match_mode') == 'superset':
#                 mock_eval.return_value = evaluation_results['superset']
#             return mock_eval
        
#         mock_create_evaluator.side_effect = create_mock_evaluator
        
#         results = run_trajectory_evaluations(actual_outputs, reference_outputs, user_message)
        
#         # Verify all evaluation modes were executed
#         expected_modes = ['unordered', 'subset', 'superset', 'unordered_with_overrides']
#         assert set(results.keys()) == set(expected_modes)
#         assert mock_create_evaluator.call_count == 4
        
#         # Verify evaluators were called with actual trajectory data
#         for call in mock_create_evaluator.call_args_list:
#             assert call[1] is not None  # Verify kwargs exist
        
#         for mode in expected_modes:
#             assert results[mode] == evaluation_results[mode]

#     @patch('src.essay_agent.graph.evaluation.create_trajectory_match_evaluator')
#     def test_tool_args_match_overrides_with_actual_data(self, mock_create_evaluator, actual_outputs_cache):
#         """Test tool arguments matching with custom overrides using actual data"""
#         user_message = "find 5 related news articles on walmart"
#         actual_outputs = actual_outputs_cache(user_message)
        
#         mock_evaluator = Mock()
#         mock_evaluator.return_value = {
#             'score': True,
#             'reasoning': 'Tool arguments match with custom comparison',
#             'tool_args_matched': True
#         }
#         mock_create_evaluator.return_value = mock_evaluator
        
#         results = run_trajectory_evaluations(actual_outputs, actual_outputs, user_message)
        
#         # Verify evaluator with overrides was created
#         calls = mock_create_evaluator.call_args_list
#         override_call = None
#         for call in calls:
#             if 'tool_args_match_overrides' in call.kwargs:
#                 override_call = call
#                 break
        
#         assert override_call is not None
#         assert override_call.kwargs['trajectory_match_mode'] == 'unordered'
        
#         # Verify the custom comparison function exists
#         if 'get_related_news_tool' in override_call.kwargs['tool_args_match_overrides']:
#             override_func = override_call.kwargs['tool_args_match_overrides']['get_related_news_tool']
#             # Test case insensitive matching
#             assert override_func({"topic": "Trump"}, {"topic": "trump"}) is True
#             assert override_func({"topic": "Biden"}, {"topic": "trump"}) is False

#     @patch('src.essay_agent.graph.evaluation.create_trajectory_match_evaluator')
#     def test_evaluation_error_handling_with_actual_data(self, mock_create_evaluator, actual_outputs_cache):
#         """Test error handling in trajectory evaluations with actual data"""
#         user_message = "find 5 related news articles on walmart"
#         actual_outputs = actual_outputs_cache(user_message)
        
#         def create_evaluator_with_error(*args, **kwargs):
#             mock_eval = Mock()
#             if kwargs.get('trajectory_match_mode') == 'subset':
#                 mock_eval.side_effect = Exception("Evaluation failed")
#             else:
#                 mock_eval.return_value = {'score': True, 'reasoning': 'Success'}
#             return mock_eval
        
#         mock_create_evaluator.side_effect = create_evaluator_with_error
        
#         results = run_trajectory_evaluations(actual_outputs, actual_outputs, user_message)
        
#         # Verify that failing evaluation returns None
#         assert results['subset'] is None
#         # Verify other evaluations still work
#         assert results['unordered'] is not None
#         assert results['superset'] is not None
#         assert results['unordered_with_overrides'] is not None


# class TestEvaluateToolUsage:
#     """Test cases for evaluate_tool_usage function"""
    
#     @patch('src.essay_agent.graph.evaluation.get_reference_outputs')
#     @patch('src.essay_agent.graph.evaluation.run_trajectory_evaluations')
#     def test_evaluate_tool_usage_with_reference(self, mock_run_trajectory, mock_get_reference):
#         """Test evaluate_tool_usage with provided reference outputs"""
#         user_message = "find 5 related news articles on walmart"
        
#         # Get actual outputs by running the workflow once
#         actual_outputs, _ = evaluate_tool_usage(user_message)
#         mock_reference = actual_outputs  # Use actual outputs as reference
#         mock_trajectory_results = {'unordered': {'score': True}}
        
#         # Setup mocks
#         mock_run_trajectory.return_value = mock_trajectory_results
        
#         # Execute function with provided reference
#         outputs, trajectory_results = evaluate_tool_usage(user_message, mock_reference)
        
#         # Verify trajectory evaluation was run with provided reference
#         mock_run_trajectory.assert_called_once()
        
#         # Verify reference outputs were not fetched from storage
#         mock_get_reference.assert_not_called()
        
#         # Verify results
#         assert outputs is not None
#         assert isinstance(outputs, list)
#         assert trajectory_results == mock_trajectory_results

#     @patch('src.essay_agent.graph.evaluation.get_reference_outputs')
#     def test_evaluate_tool_usage_no_reference_found(self, mock_get_reference):
#         """Test evaluate_tool_usage when no reference output is found"""
#         user_message = "completely unknown message for testing"
        
#         # Setup mocks - no reference found
#         mock_get_reference.return_value = {}  # Empty reference data
        
#         # Execute function
#         outputs, trajectory_results = evaluate_tool_usage(user_message)
        
#         # Verify that empty results are returned when no reference is found
#         assert outputs is not None
#         assert isinstance(outputs, list)
#         assert trajectory_results == {}


# class TestActualTrajectoryData:
#     """Test cases that verify actual trajectory data structure and tool extraction"""
    
#     def test_actual_trajectory_structure(self):
#         """Test that actual trajectory has expected structure"""
#         user_message = "find 5 related news articles on walmart"
        
#         # Get actual trajectory data
#         outputs, _ = evaluate_tool_usage(user_message)
        
#         # Verify basic structure
#         assert outputs is not None
#         assert isinstance(outputs, list)
#         assert len(outputs) > 0
        
#         # Verify user message is present
#         user_messages = [msg for msg in outputs if msg.get('role') == 'user']
#         assert len(user_messages) > 0
#         assert any(user_message in msg.get('content', '') for msg in user_messages)

#     def test_tool_extraction_from_actual_outputs(self):
#         """Test tool extraction from actual workflow outputs"""
#         user_message = "find 5 related news articles on trump , then review the summary for accuracy and coherence."
        
#         # Execute actual workflow
#         outputs, _ = evaluate_tool_usage(user_message)
        
#         # Extract tool names from actual outputs
#         actual_tool_names = []
#         for message in outputs:
#             if isinstance(message, dict) and 'tool_calls' in message:
#                 for tool_call in message.get('tool_calls', []):
#                     if isinstance(tool_call, dict) and 'function' in tool_call:
#                         actual_tool_names.append(tool_call['function']['name'])
        
#         # Verify expected patterns are present
#         expected_patterns = ['transfer', 'agent']
#         assert any(any(pattern in tool_name.lower() for pattern in expected_patterns) 
#                   for tool_name in actual_tool_names), f"Expected patterns not found in {actual_tool_names}"

#     def test_tool_arguments_extraction(self):
#         """Test extraction of tool arguments from actual trajectory"""
#         user_message = "find 5 related news articles on walmart"
        
#         # Get actual trajectory
#         outputs, _ = evaluate_tool_usage(user_message)
        
#         # Extract all tool arguments
#         all_tool_args = []
#         for message in outputs:
#             if isinstance(message, dict) and 'tool_calls' in message:
#                 for tool_call in message.get('tool_calls', []):
#                     if isinstance(tool_call, dict) and 'function' in tool_call:
#                         try:
#                             args = json.loads(tool_call['function']['arguments'])
#                             all_tool_args.append({
#                                 'tool_name': tool_call['function']['name'],
#                                 'arguments': args
#                             })
#                         except (json.JSONDecodeError, TypeError):
#                             # Handle cases where arguments aren't JSON
#                             all_tool_args.append({
#                                 'tool_name': tool_call['function']['name'],
#                                 'arguments': tool_call['function']['arguments']
#                             })
        
#         # Verify structure of extracted arguments
#         for tool_arg in all_tool_args:
#             assert 'tool_name' in tool_arg
#             assert 'arguments' in tool_arg

#     @pytest.mark.parametrize("test_topic,reference_topic,expected", [
#         ("Trump", "trump", True),
#         ("WALMART", "walmart", True),
#         ("Biden", "trump", False),
#     ])
#     def test_topic_matching_scenarios(self, test_topic, reference_topic, expected):
#         """Test topic matching scenarios without running workflows"""
#         topic_matcher = lambda x, y: x.get("topic", "").lower() == y.get("topic", "").lower()
        
#         test_args = {"topic": test_topic}
#         reference_args = {"topic": reference_topic}
        
#         assert topic_matcher(test_args, reference_args) == expected
import pytest
from src.essay_agent.graph.evaluation import evaluate_tool_usage, run_trajectory_evaluations


class TestTrajectoryEvaluationsRealRun:
    """Test cases for trajectory evaluation functions with real workflow execution"""
    
    def test_trump_trajectory_evaluation_pass_threshold(self):
        """Test Trump news search trajectory evaluation meets pass threshold (>=2 out of 4)"""
        user_message = "find 5 related news articles on trump , then review the summary for accuracy and coherence."
        
        # Get actual trajectory by running the workflow
        actual_outputs, _ = evaluate_tool_usage(user_message)
        
        # Use same outputs as reference for this test
        reference_outputs =  [{'role': 'user', 'content': 'find 5 related news articles on trump , then review the summary for accuracy and coherence.'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_5Tt4zb0acW674cX7xm5HBJzw', 'function': {'name': 'transfer_to_work_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_work_agent', 'tool_call_id': 'call_5Tt4zb0acW674cX7xm5HBJzw', 'content': 'Successfully transferred to work_agent'}, {'role': 'assistant', 'name': 'work_agent', 'content': 'Here are the top 5 related news articles on Trump:\n\n### 1. Morning Report — Trump sprints to the high court with emergency appeals\n**Summary:** This article discusses former President Donald Trump\'s recent emergency appeals to the Supreme Court. The appeals are part of his ongoing legal battles and efforts to overturn various decisions.\n**Source:** [The Hill](https://thehill.com/newsletters/morning-report/5329781-donald-trump-high-court-appeals/)\n**Date:** 24 days ago\n\n### 2. Trump says Musk will face \'serious consequences\' if he funds Democratic candidates\n**Summary:** In a phone interview with NBC News, Trump warned Elon Musk of "serious consequences" if he funds Democratic candidates. The article highlights the tension between Trump and Musk, with Trump criticizing Musk\'s involvement in politics.\n**Source:** [NBC News](https://www.nbcnews.com/politics/donald-trump/trump-elon-musk-consequences-funds-democratic-candidates-rcna211605)\n**Date:** 20 days ago\n\n### 3. Read Trump’s memo asking Congress to take back approved funding for foreign aid, PBS, NPR\n**Summary:** This article provides details on Trump\'s memo to Congress requesting the rescission of approved funding for foreign aid, PBS, and NPR. The memo is part of Trump\'s broader efforts to cut government spending on what he deems unnecessary programs.\n**Source:** [PBS](https://www.pbs.org/newshour/politics/read-trumps-full-memo-asking-congress-to-claw-back-approved-spending-targeted-by-doge)\n**Date:** 24 days ago\n\n### 4. Trump administration presents details of budget cuts\n**Summary:** The Trump administration has proposed significant budget cuts to federal housing and health care programs, while increasing funding for the military. The proposed budget also includes cuts to Amtrak and other federal programs.\n**Source:** [NJ Spotlight News](https://www.njspotlightnews.org/2025/06/new-documents-show-extent-of-trump-administrations-budget-cutting-aims/)\n**Date:** 23 days ago\n\n### 5. Trump and Musk\'s relationship flames out just as intensely as it started\n**Summary:** The article describes the fallout between Trump and Elon Musk, highlighting their initial strong alliance and subsequent public disputes. The conflict has escalated to threats and accusations from both sides.\n**Source:** [AP News](https://apnews.com/article/trump-musk-tax-bill-6e7845081259c34db785182c51569c0c)\n**Date:** 22 days ago\n\nThese articles provide a comprehensive overview of recent news related to Donald Trump, covering his legal battles, political conflicts, budget proposals, and more.'}, {'role': 'assistant', 'name': 'work_agent', 'tool_calls': [{'type': 'function', 'id': '7f5b1085-a706-4167-97ee-98264f4b8123', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '7f5b1085-a706-4167-97ee-98264f4b8123', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_fOBty65UyXaGTgfAtAtBZnYX', 'function': {'name': 'transfer_to_review_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_review_agent', 'tool_call_id': 'call_fOBty65UyXaGTgfAtAtBZnYX', 'content': 'Successfully transferred to review_agent'}, {'role': 'assistant', 'name': 'review_agent', 'content': "Here is the detailed feedback on the summaries of the five articles related to Trump:\n\n### 1. Morning Report — Trump sprints to the high court with emergency appeals\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary is concise but lacks specific details about the nature of the decisions Trump is trying to overturn and the legal arguments presented.\n- **Accuracy:** The summary accurately reflects the general topic of the article.\n- **Quality:** The summary is clear but could be more engaging with additional context.\n- **Specific Issues:** Adding more context about the specific cases and potential implications would improve the summary.\n\n### 2. Trump says Musk will face 'serious consequences' if he funds Democratic candidates\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks context and detail about the background and significance of the situation.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more informative with additional context and quotes.\n- **Specific Issues:** Including more context about the tension between Trump and Musk, as well as direct quotes, would enhance the summary.\n\n### 3. Read Trump’s memo asking Congress to take back approved funding for foreign aid, PBS, NPR\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks details about the rationale behind the memo and the potential impact of the proposed cuts.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more informative with additional context and perspectives.\n- **Specific Issues:** Adding context about the rationale for the cuts, potential impacts, and perspectives from both supporters and critics would improve the summary.\n\n### 4. Trump administration presents details of budget cuts\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks details about the rationale behind the budget changes and their potential impact.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more informative with additional context and specifics.\n- **Specific Issues:** Including context about the rationale for the budget changes, potential impacts, and specific figures would enhance the summary.\n\n### 5. Trump and Musk's relationship flames out just as intensely as it started\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks specific details about the nature of the initial alliance and the specific incidents that led to the fallout.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more engaging with additional context and quotes.\n- **Specific Issues:** Adding background information, details about the disputes, direct quotes, and contextualizing the conflict would improve the summary.\n\nOverall, the summaries provide a good foundation but could be enhanced with additional details, context, and perspectives to make them more informative and engaging for readers."}, {'role': 'assistant', 'name': 'review_agent', 'tool_calls': [{'type': 'function', 'id': '413ccd11-86ba-40c2-a74a-8338ae438a8d', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '413ccd11-86ba-40c2-a74a-8338ae438a8d', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'content': 'The review of the summaries is complete. The feedback highlights areas for improvement in terms of adding more context, details, and perspectives to make the summaries more informative and engaging. If you need any further assistance or revisions, please let me know!'}],
       
        
        # Run trajectory evaluations with real data
        results = run_trajectory_evaluations(actual_outputs, reference_outputs, user_message)
        
        # Count True scores from the 4 evaluation modes
        true_scores = 0
        evaluation_modes = ['unordered', 'subset', 'superset', 'unordered_with_overrides']
        
        for mode in evaluation_modes:
            if results.get(mode) and results[mode].get('score') is True:
                true_scores += 1
        
        # Print results for verification
        print(f"Trump trajectory evaluation results:")
        for mode in evaluation_modes:
            score = results.get(mode, {}).get('score', 'None')
            print(f"  {mode}: {score}")
        print(f"Total True scores: {true_scores}/4")
        
        # Assert that at least 2 out of 4 evaluations are True (pass threshold)
        assert true_scores >= 2, f"Expected at least 2 True scores out of 4, got {true_scores}"
        
        # Verify all expected modes are present
        for mode in evaluation_modes:
            assert mode in results, f"Missing evaluation mode: {mode}"

    def test_walmart_trajectory_evaluation_pass_threshold(self):
        """Test Walmart news search trajectory evaluation meets pass threshold (>=2 out of 4)"""
        user_message = "find 5 related news articles on walmart"
        
        # Get actual trajectory by running the workflow
        actual_outputs, _ = evaluate_tool_usage(user_message)
        
        # Use same outputs as reference for this test
        reference_outputs = [{'role': 'user', 'content': 'find 5 related news articles on walmart'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_UXF8Bpqr5MGoQiqGHJJVXOOf', 'function': {'name': 'transfer_to_work_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_work_agent', 'tool_call_id': 'call_UXF8Bpqr5MGoQiqGHJJVXOOf', 'content': 'Successfully transferred to work_agent'}, {'role': 'assistant', 'name': 'work_agent', 'content': '### Top 5 Related News Articles on Walmart\n\n#### 1. Walmart Takes Flight With Drone Delivery Expansion to Five New Cities, Redefining Fast, Flexible Retail\n- **Summary**: Walmart is expanding its drone delivery service to five new cities, including Atlanta, Charlotte, Houston, Orlando, and Tampa. This expansion, in partnership with Wing, aims to provide faster and more efficient delivery services.\n- **Source**: [Walmart](https://corporate.walmart.com/news/2025/06/05/walmart-takes-flight-with-drone-delivery-expansion-to-5-new-cities-redefining-fast-flexible-retail)\n- **Date**: 21 days ago\n\n#### 2. Walmart to Expand Drone Delivery to 5 More Cities\n- **Summary**: Walmart, in collaboration with Wing, is set to expand its drone delivery program to five additional cities, reaching millions of new customers. The service will include thousands of items, such as fresh produce and household essentials.\n- **Source**: [Supply Chain Dive](https://www.supplychaindive.com/news/walmart-wing-drone-delivery-availability-expansion/750072/)\n- **Date**: 20 days ago\n\n#### 3. Walmart Challenges Consumer Perceptions with ‘Who Knew?’ Campaign\n- **Summary**: Walmart has launched a new campaign, "Who Knew?", featuring actors Walton Goggins and Stephanie Beatriz. The campaign aims to challenge consumer perceptions and highlight the various perks of shopping at Walmart.\n- **Source**: [Marketing Dive](https://www.marketingdive.com/news/walmart-challenges-consumer-perceptions-with-who-knew-campaign/750112/)\n- **Date**: 17 days ago\n\n#### 4. Walmart CEO McMillon Talks Wages, Worker Education, and Tariffs\n- **Summary**: Walmart CEO Doug McMillon discussed the company\'s efforts to raise wages, invest in worker education, and navigate tariffs. He highlighted significant wage increases and investments in skills training and education programs.\n- **Source**: [Talk Business & Politics](https://talkbusiness.net/2025/06/walmart-ceo-mcmillon-talks-wages-worker-education-and-tariffs/)\n- **Date**: 20 days ago\n\n#### 5. Walmart Debuts Sparky, Its Generative AI Assistant for Customers\n- **Summary**: Walmart has introduced Sparky, a generative AI assistant designed to help customers by summarizing reviews, offering recommendations, and assisting with purchase planning. This initiative is part of Walmart\'s broader AI integration plans.\n- **Source**: [Retail Dive](https://www.retaildive.com/news/walmart-launches-generative-ai-assistant-sparky/750300/)\n- **Date**: 16 days ago\n\nThese articles provide a comprehensive overview of Walmart\'s recent initiatives and developments, including technological advancements, marketing campaigns, and corporate strategies.'}, {'role': 'assistant', 'name': 'work_agent', 'tool_calls': [{'type': 'function', 'id': '3ccd1290-249d-4ea5-9f6d-a6da4d47e366', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '3ccd1290-249d-4ea5-9f6d-a6da4d47e366', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'content': 'The work_agent has found 5 related news articles on Walmart. Would you like the review_agent to critique the generated content?'}]
          
        
        # Run trajectory evaluations with real data
        results = run_trajectory_evaluations(actual_outputs, reference_outputs, user_message)
        
        # Count True scores from the 4 evaluation modes
        true_scores = 0
        evaluation_modes = ['unordered', 'subset', 'superset', 'unordered_with_overrides']
        
        for mode in evaluation_modes:
            if results.get(mode) and results[mode].get('score') is True:
                true_scores += 1
        
        # Print results for verification
        print(f"Walmart trajectory evaluation results:")
        for mode in evaluation_modes:
            score = results.get(mode, {}).get('score', 'None')
            print(f"  {mode}: {score}")
        print(f"Total True scores: {true_scores}/4")
        
        # Assert that at least 2 out of 4 evaluations are True (pass threshold)
        assert true_scores >= 2, f"Expected at least 2 True scores out of 4, got {true_scores}"
        
        # Verify all expected modes are present
        for mode in evaluation_modes:
            assert mode in results, f"Missing evaluation mode: {mode}"