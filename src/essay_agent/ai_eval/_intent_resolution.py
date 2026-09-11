import os
import math
import json
import yaml
import re
from typing import Dict, Union, List, Optional

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

from src.essay_agent.llm.llm_proxy import setup_llm
from src.essay_agent.configs.app_config import settings


class IntentResolutionEvaluator:
    """
    Evaluates intent resolution for a given query and response or a multi-turn conversation,
    including reasoning, using your own LLM client.
    """

    _MIN_INTENT_RESOLUTION_SCORE = 1
    _MAX_INTENT_RESOLUTION_SCORE = 5
    _DEFAULT_INTENT_RESOLUTION_THRESHOLD = 3
    _RESULT_KEY = "intent_resolution"

    def __init__(self, threshold: float = _DEFAULT_INTENT_RESOLUTION_THRESHOLD, **kwargs):
        self.threshold = threshold
        # initialize your LLM client
        self.llm = setup_llm()
        self._prompt_template = self._create_evaluation_template()

    def _create_evaluation_template(self) -> ChatPromptTemplate:
        """Create a template that asks for structured text output instead of JSON"""
        system = """You are an expert in evaluating the quality of responses from intelligent assistants. Your task is to assess whether the assistant's response adequately addresses the user's intent.

Evaluation Criteria:
- Intent Understanding: How well did the assistant understand what the user wanted?
- Response Completeness: Does the response fully address all aspects of the query?
- Tool Usage: If tools were available, were they used appropriately to fulfill the user's request?
- Tool Call Analysis: Were the right tools called with appropriate parameters?
- Accuracy: Is the information provided correct and relevant?

Scoring Scale:
- Score 1: Response completely unrelated to user intent
- Score 2: Response minimally relates to user intent  
- Score 3: Response partially addresses the user intent but lacks complete details
- Score 4: Response addresses the user intent with moderate accuracy but has minor gaps
- Score 5: Response directly addresses the user intent and fully resolves it

You must respond in this EXACT format:
SCORE: [number from 1-5]
EXPLANATION: [detailed explanation of your scoring decision]
INTENT_DETECTED: [YES/NO - whether you think the assistant correctly identified the user's intent]
INTENT_RESOLVED: [YES/NO - whether the user's intent was fully resolved]
USER_INTENT: [brief description of what you think the user actually wanted]
AGENT_INTENT: [brief description of what you think the agent understood the user wanted]"""

        user = """Evaluate the following interaction:

USER QUERY: {query}

ASSISTANT RESPONSE: {response}

TOOL CALLS MADE: {tool_calls}

AVAILABLE TOOLS: {tool_definitions}

Please provide your evaluation using the exact format specified in the system prompt."""

        return ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", user)
        ])

    def _format_messages(self, msgs: Union[str, List[dict]]) -> str:
        """Format messages for display"""
        if isinstance(msgs, str):
            return msgs
        
        if not msgs:
            return "No messages"
            
        out = []
        for m in msgs:
            if isinstance(m, dict):
                role = m.get("role", "unknown").title()
                content = m.get("content", "")
                if isinstance(content, list):
                    # Handle complex content structures
                    parts = []
                    for p in content:
                        if isinstance(p, dict):
                            if p.get("type") == "text":
                                parts.append(p.get("text", ""))
                            elif p.get("type") == "tool_call":
                                fn = p.get("tool_call", {}).get("function", {})
                                parts.append(f"Tool Call: {fn.get('name', 'unknown')}({fn.get('arguments', '')})")
                            elif p.get("type") == "tool_result":
                                parts.append(f"Tool Result: {p.get('tool_result', '')}")
                        else:
                            parts.append(str(p))
                    content = " | ".join(parts)
                out.append(f"{role}: {content}")
            else:
                out.append(str(m))
        return "\n".join(out)

    def _format_tool_calls(self, tool_calls: Optional[Union[str, List[dict], dict]]) -> str:
        """Format tool calls for display"""
        if not tool_calls:
            return "No tool calls made"
        
        if isinstance(tool_calls, str):
            return tool_calls
            
        if isinstance(tool_calls, dict):
            tool_calls = [tool_calls]
        
        try:
            formatted_calls = []
            for call in tool_calls:
                if isinstance(call, dict):
                    tool_name = call.get('name', 'unknown_tool')
                    args = call.get('arguments', call.get('args', {}))
                    formatted_calls.append(f"Tool: {tool_name}, Arguments: {json.dumps(args) if isinstance(args, dict) else str(args)}")
                else:
                    formatted_calls.append(str(call))
            return "\n".join(formatted_calls)
        except:
            return str(tool_calls)

    def _format_tools(self, tools: Optional[Union[dict, List[dict]]]) -> str:
        """Format tool definitions for display"""
        if not tools:
            return "No tools available"
        if isinstance(tools, dict):
            tools = [tools]
        
        try:
            return json.dumps(tools, indent=2)
        except:
            return str(tools)

    def _parse_text_response(self, txt: str) -> dict:
        """Parse structured text response from LLM"""
        # Initialize default values
        result = {
            "resolution_score": self._MIN_INTENT_RESOLUTION_SCORE,
            "explanation": "Could not parse evaluation response",
            "conversation_has_intent": True,
            "agent_perceived_intent": "unknown",
            "actual_user_intent": "unknown", 
            "correct_intent_detected": False,
            "intent_resolved": False
        }
        
        try:
            # Extract score
            score_match = re.search(r'SCORE:\s*(\d+)', txt, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                if self._MIN_INTENT_RESOLUTION_SCORE <= score <= self._MAX_INTENT_RESOLUTION_SCORE:
                    result["resolution_score"] = float(score)
            
            # Extract explanation
            explanation_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n[A-Z_]+:|$)', txt, re.IGNORECASE | re.DOTALL)
            if explanation_match:
                result["explanation"] = explanation_match.group(1).strip()
            
            # Extract intent detection
            intent_detected_match = re.search(r'INTENT_DETECTED:\s*(YES|NO)', txt, re.IGNORECASE)
            if intent_detected_match:
                result["correct_intent_detected"] = intent_detected_match.group(1).upper() == "YES"
            
            # Extract intent resolution
            intent_resolved_match = re.search(r'INTENT_RESOLVED:\s*(YES|NO)', txt, re.IGNORECASE)
            if intent_resolved_match:
                result["intent_resolved"] = intent_resolved_match.group(1).upper() == "YES"
            
            # Extract user intent
            user_intent_match = re.search(r'USER_INTENT:\s*(.+?)(?=\n[A-Z_]+:|$)', txt, re.IGNORECASE | re.DOTALL)
            if user_intent_match:
                result["actual_user_intent"] = user_intent_match.group(1).strip()
            
            # Extract agent intent
            agent_intent_match = re.search(r'AGENT_INTENT:\s*(.+?)(?=\n[A-Z_]+:|$)', txt, re.IGNORECASE | re.DOTALL)
            if agent_intent_match:
                result["agent_perceived_intent"] = agent_intent_match.group(1).strip()
                
        except Exception as e:
            result["explanation"] = f"Error parsing response: {str(e)}. Raw response: {txt[:200]}{'...' if len(txt) > 200 else ''}"
        
        return result

    def _get_default_tool_definitions(self) -> List[dict]:
        """Get default tool definitions for evaluation"""
        return [
            # Document tools
            {
                "name": "document_tools",
                "description": "Takes a document and summarizes its content, answering specific questions about the document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document": {"type": "string", "description": "The document content to analyze"},
                        "questions": {"type": "array", "items": {"type": "string"}, "description": "Specific questions to answer about the document"}
                    },
                    "required": ["document"]
                }
            },
           
            # News tools
            {
                "name": "news_tools",
                "description": "Searches for and returns related news articles based on a given topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "The topic to search for news articles about"},
                        "count": {"type": "integer", "description": "Number of articles to return", "default": 5},
                        "date_range": {"type": "string", "description": "Date range for news articles", "default": "last_week"}
                    },
                    "required": ["topic"]
                }
            },
            
            # Critic tools
            {
                "name": "critic_tools",
                "description": "Reviews generated content for accuracy and factual correctness",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "The content to review for accuracy"},
                        "source_material": {"type": "string", "description": "Source material to verify accuracy against"}
                    },
                    "required": ["content"]
                }
            },
            
        ]

    def _format_messages(self, msgs: Union[str, List[dict]]) -> str:
        """Format messages for display"""
        if isinstance(msgs, str):
            return msgs
        
        if not msgs:
            return "No messages"
            
        out = []
        for m in msgs:
            if isinstance(m, dict):
                role = m.get("role", "unknown").title()
                content = m.get("content", "")
                if isinstance(content, list):
                    # Handle complex content structures
                    parts = []
                    for p in content:
                        if isinstance(p, dict):
                            if p.get("type") == "text":
                                parts.append(p.get("text", ""))
                            elif p.get("type") == "tool_call":
                                fn = p.get("tool_call", {}).get("function", {})
                                parts.append(f"Tool Call: {fn.get('name', 'unknown')}({fn.get('arguments', '')})")
                            elif p.get("type") == "tool_result":
                                parts.append(f"Tool Result: {p.get('tool_result', '')}")
                        else:
                            parts.append(str(p))
                    content = " | ".join(parts)
                out.append(f"{role}: {content}")
            else:
                out.append(str(m))
        return "\n".join(out)

    def _format_tool_calls(self, tool_calls: Optional[Union[str, List[dict], dict]]) -> str:
        """Format tool calls for display"""
        if not tool_calls:
            return "No tool calls made"
        
        if isinstance(tool_calls, str):
            return tool_calls
            
        if isinstance(tool_calls, dict):
            tool_calls = [tool_calls]
        
        try:
            formatted_calls = []
            for call in tool_calls:
                if isinstance(call, dict):
                    tool_name = call.get('name', 'unknown_tool')
                    args = call.get('arguments', call.get('args', {}))
                    formatted_calls.append(f"Tool: {tool_name}, Arguments: {json.dumps(args) if isinstance(args, dict) else str(args)}")
                else:
                    formatted_calls.append(str(call))
            return "\n".join(formatted_calls)
        except:
            return str(tool_calls)

    def _format_tools(self, tools: Optional[Union[dict, List[dict]]]) -> str:
        """Format tool definitions for display"""
        if not tools:
            return "No tools available"
        if isinstance(tools, dict):
            tools = [tools]
        
        try:
            return json.dumps(tools, indent=2)
        except:
            return str(tools)

    def _parse_text_response(self, txt: str) -> dict:
        """Parse structured text response from LLM"""
        # Initialize default values
        result = {
            "resolution_score": self._MIN_INTENT_RESOLUTION_SCORE,
            "explanation": "Could not parse evaluation response",
            "conversation_has_intent": True,
            "agent_perceived_intent": "unknown",
            "actual_user_intent": "unknown", 
            "correct_intent_detected": False,
            "intent_resolved": False
        }
        
        try:
            # Extract score
            score_match = re.search(r'SCORE:\s*(\d+)', txt, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                if self._MIN_INTENT_RESOLUTION_SCORE <= score <= self._MAX_INTENT_RESOLUTION_SCORE:
                    result["resolution_score"] = float(score)
            
            # Extract explanation
            explanation_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n[A-Z_]+:|$)', txt, re.IGNORECASE | re.DOTALL)
            if explanation_match:
                result["explanation"] = explanation_match.group(1).strip()
            
            # Extract intent detection
            intent_detected_match = re.search(r'INTENT_DETECTED:\s*(YES|NO)', txt, re.IGNORECASE)
            if intent_detected_match:
                result["correct_intent_detected"] = intent_detected_match.group(1).upper() == "YES"
            
            # Extract intent resolution
            intent_resolved_match = re.search(r'INTENT_RESOLVED:\s*(YES|NO)', txt, re.IGNORECASE)
            if intent_resolved_match:
                result["intent_resolved"] = intent_resolved_match.group(1).upper() == "YES"
            
            # Extract user intent
            user_intent_match = re.search(r'USER_INTENT:\s*(.+?)(?=\n[A-Z_]+:|$)', txt, re.IGNORECASE | re.DOTALL)
            if user_intent_match:
                result["actual_user_intent"] = user_intent_match.group(1).strip()
            
            # Extract agent intent
            agent_intent_match = re.search(r'AGENT_INTENT:\s*(.+?)(?=\n[A-Z_]+:|$)', txt, re.IGNORECASE | re.DOTALL)
            if agent_intent_match:
                result["agent_perceived_intent"] = agent_intent_match.group(1).strip()
                
        except Exception as e:
            result["explanation"] = f"Error parsing response: {str(e)}. Raw response: {txt[:200]}{'...' if len(txt) > 200 else ''}"
        
        return result

    

    def __call__(
        self,
        *,
        query: Union[str, List[dict]],
        response: Union[str, List[dict]],
        tool_calls: Optional[Union[str, List[dict], dict]] = None,
        tool_definitions: Optional[Union[dict, List[dict]]] = None
    ) -> Dict[str, Union[float, str, bool]]:
        try:
            # Use default tool definitions if none provided
            if tool_definitions is None:
                tool_definitions = self._get_default_tool_definitions()
            
            # Format inputs
            q = self._format_messages(query)
            r = self._format_messages(response)
            tc = self._format_tool_calls(tool_calls)
            t = self._format_tools(tool_definitions)

            # Generate prompt and get LLM response
            prompt = self._prompt_template.format(
                query=q, response=r, tool_calls=tc, tool_definitions=t
            )
            
            llm_resp = self.llm.invoke(prompt)
            txt = getattr(llm_resp, "content", str(llm_resp))
            if isinstance(txt, list):
                txt = "".join(block.get("text", "") if isinstance(block, dict) else str(block) for block in txt)
            
            # Parse the structured text response
            parsed_result = self._parse_text_response(txt)
            
            score = parsed_result.get("resolution_score", self._MIN_INTENT_RESOLUTION_SCORE)
            explanation = parsed_result.get("explanation", "No explanation provided")
            
            # Determine pass/fail
            result = "pass" if score >= self.threshold else "fail"

            # Prepare additional details
            details = {
                "raw_llm_response": txt,
                "formatted_query": q[:500] + "..." if len(q) > 500 else q,
                "formatted_response": r[:500] + "..." if len(r) > 500 else r,
                "formatted_tool_calls": tc[:500] + "..." if len(tc) > 500 else tc,
                "evaluation_threshold": self.threshold,
                "parsed_details": parsed_result
            }

            return {
                self._RESULT_KEY: score,
                f"{self._RESULT_KEY}_result": result,
                f"{self._RESULT_KEY}_threshold": self.threshold,
                f"{self._RESULT_KEY}_reason": explanation,
                "additional_details": details,
                # Add individual fields for easier access
                "conversation_has_intent": parsed_result.get("conversation_has_intent", True),
                "agent_perceived_intent": parsed_result.get("agent_perceived_intent", "unknown"),
                "actual_user_intent": parsed_result.get("actual_user_intent", "unknown"),
                "correct_intent_detected": parsed_result.get("correct_intent_detected", False),
                "intent_resolved": parsed_result.get("intent_resolved", False)
            }

        except Exception as e:
            return {
                self._RESULT_KEY: float(self._MIN_INTENT_RESOLUTION_SCORE),
                f"{self._RESULT_KEY}_result": "fail",
                f"{self._RESULT_KEY}_threshold": self.threshold,
                f"{self._RESULT_KEY}_reason": f"Evaluation error: {str(e)}",
                "additional_details": {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                "conversation_has_intent": True,
                "agent_perceived_intent": "unknown",
                "actual_user_intent": "unknown",
                "correct_intent_detected": False,
                "intent_resolved": False
            }