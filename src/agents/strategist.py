"""
Agent 1: The Strategist

Role: Search for raw pain points in the market.
Uses: LangGraph Tools + VADER Sentiment Analysis

The Strategist is the first agent in the pipeline. It:
1. Takes the raw idea as input
2. Uses tools autonomously to search community platforms and market data
3. Applies sentiment analysis to filter genuine pain
4. Outputs a list of raw_pains for the Critic to verify
"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.graph.state import MarketState
from src.config.prompts import STRATEGIST_PROMPT
from src.utils.llm import get_research_llm
from src.utils.sentiment import filter_genuine_pains, analyze_pain_points
from src.tools import get_tools_for_agent
from src.tools.search import build_search_queries


def run_strategist(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Strategist agent with autonomous tool usage.
    
    Inputs from state:
        - raw_idea: The startup idea to research
        - target_region: Geographic focus (default: India)
        - critic_feedback: If looping, what to improve
    
    Outputs to state:
        - raw_pains: List of potential pain points with sentiment scores
    """
    idea = state.get("raw_idea", "")
    region = state.get("target_region", "India")
    feedback = state.get("critic_feedback", "")
    
    # Get tools for this agent
    tools = get_tools_for_agent("strategist")
    
    # Build suggested search queries
    suggested_queries = build_search_queries(idea, region)
    
    # Add feedback context if we're in a loop
    feedback_context = ""
    if feedback:
        feedback_context = f"\n\n⚠️ PREVIOUS FEEDBACK FROM CRITIC:\n{feedback}\nPlease address these gaps by searching more thoroughly."
    
    # Bind tools to LLM
    llm = get_research_llm()
    llm_with_tools = llm.bind_tools(tools)
    
    # Initial prompt
    messages = [
        SystemMessage(content=STRATEGIST_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}
REGION: {region}

TASK: Research pain points for this startup idea.

SUGGESTED QUERIES (use these or create your own):
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(suggested_queries[:5]))}
{feedback_context}

Use the available tools to:
1. Search community platforms (Reddit, Twitter, Quora) for user complaints
2. Search Indian news/startup sources for market data and statistics
3. Call tools multiple times with different queries to get comprehensive data

After gathering search results, extract the raw pain points as JSON.
Return your response as valid JSON matching the output format specified in your system prompt.
""")
    ]
    
    # Agentic loop: Let LLM call tools until it has enough data
    max_iterations = 5
    for iteration in range(max_iterations):
        response = llm_with_tools.invoke(messages)
        
        # Check if LLM wants to call tools
        if not response.tool_calls:
            # No more tool calls, LLM has final answer
            break
        
        # Execute tool calls
        messages.append(response)
        
        for tool_call in response.tool_calls:
            # Find the tool
            tool = next((t for t in tools if t.name == tool_call["name"]), None)
            if tool:
                # Execute the tool
                tool_result = tool.invoke(tool_call["args"])
                
                # Add tool response to conversation
                from langchain_core.messages import ToolMessage
                messages.append(ToolMessage(
                    content=json.dumps(tool_result),
                    tool_call_id=tool_call["id"]
                ))
    
    # Parse final LLM response
    try:
        content = response.content if isinstance(response, AIMessage) else str(response)
        # Find JSON in the response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(content[json_start:json_end])
            raw_pains = parsed.get("raw_pains", [])
        else:
            raw_pains = []
    except (json.JSONDecodeError, AttributeError):
        raw_pains = []
    
    # Apply sentiment analysis to filter genuine pains
    if raw_pains:
        analyzed_pains = analyze_pain_points(raw_pains)
        genuine_pains = filter_genuine_pains(raw_pains)
    else:
        analyzed_pains = []
        genuine_pains = []
    
    return {
        "raw_pains": analyzed_pains,  # Keep all for transparency
        "genuine_pains_count": len(genuine_pains),
    }
