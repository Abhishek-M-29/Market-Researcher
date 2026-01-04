"""
Agent 1: The Strategist

Role: Search for raw pain points in the market.
Uses: Tavily Search + VADER Sentiment Analysis

The Strategist is the first agent in the pipeline. It:
1. Takes the raw idea as input
2. Searches community platforms (Reddit, Twitter) for complaints
3. Applies sentiment analysis to filter genuine pain
4. Outputs a list of raw_pains for the Critic to verify
"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import MarketState
from src.config.prompts import STRATEGIST_PROMPT
from src.utils.llm import get_research_llm
from src.utils.sentiment import filter_genuine_pains, analyze_pain_points
from src.tools.search import (
    search_community_sources,
    search_indian_sources,
    build_search_queries
)


def run_strategist(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Strategist agent.
    
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
    
    # Build search queries
    queries = build_search_queries(idea, region)
    
    # Collect search results from multiple sources
    all_results = []
    
    # Search community platforms for complaints
    for query in queries[:3]:  # Limit to avoid rate limits
        results = search_community_sources(query, max_results=3)
        all_results.extend(results)
    
    # Search Indian news sources for market data
    for query in queries[3:5]:
        results = search_indian_sources(query, max_results=3)
        all_results.extend(results)
    
    # Prepare context for LLM
    search_context = "\n\n".join([
        f"Source: {r.get('url', 'Unknown')}\n{r.get('content', '')[:500]}"
        for r in all_results
    ])
    
    # Add feedback context if we're in a loop
    feedback_context = ""
    if feedback:
        feedback_context = f"\n\nPREVIOUS FEEDBACK FROM CRITIC:\n{feedback}\nPlease address these gaps in your research."
    
    # Call LLM to extract structured pain points (Perplexity for research)
    llm = get_research_llm()
    
    messages = [
        SystemMessage(content=STRATEGIST_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}
REGION: {region}

SEARCH RESULTS:
{search_context}
{feedback_context}

Based on the search results above, extract the raw pain points.
Remember to focus on genuine user frustrations, not mild inconveniences.

Return your response as valid JSON matching the output format specified.
""")
    ]
    
    response = llm.invoke(messages)
    
    # Parse LLM response
    try:
        # Try to extract JSON from the response
        content = response.content
        # Find JSON in the response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(content[json_start:json_end])
            raw_pains = parsed.get("raw_pains", [])
        else:
            raw_pains = []
    except json.JSONDecodeError:
        raw_pains = []
    
    # Apply sentiment analysis to filter genuine pains
    analyzed_pains = analyze_pain_points(raw_pains)
    genuine_pains = filter_genuine_pains(raw_pains)
    
    return {
        "raw_pains": analyzed_pains,  # Keep all for transparency
        "genuine_pains_count": len(genuine_pains),
    }
