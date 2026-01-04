"""
Agent 2: The Critic

Role: Verify pain points with statistical evidence.
Uses: Domain Trust Scoring + Tavily Search for verification

The Critic is the quality gate. It:
1. Takes raw_pains from the Strategist
2. Searches for statistical backing for each claim
3. Applies domain trust scoring to rate source reliability
4. Either approves (is_verified=True) or rejects with feedback
"""

import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import MarketState
from src.config.prompts import CRITIC_PROMPT
from src.utils.llm import get_research_llm
from src.utils.scoring import (
    score_pain_points,
    get_verification_feedback,
    is_claim_verified
)
from src.tools.search import search_indian_sources


def run_critic(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Critic agent.
    
    Inputs from state:
        - raw_pains: Pain points from Strategist
        - iteration_count: How many verification loops we've done
    
    Outputs to state:
        - verified_pains: Pain points with statistical backing
        - is_verified: Whether we have enough verified pains
        - critic_feedback: If not verified, what's missing
        - iteration_count: Incremented
    """
    raw_pains = state.get("raw_pains", [])
    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    idea = state.get("raw_idea", "")
    
    if not raw_pains:
        return {
            "verified_pains": [],
            "is_verified": False,
            "critic_feedback": "No pain points received from Strategist. Need to restart research.",
            "iteration_count": iteration + 1
        }
    
    # For each pain point, search for statistical evidence
    enriched_pains = []
    
    for pain in raw_pains:
        pain_text = pain.get("pain", "")
        
        # Skip if already verified or has stats
        if pain.get("stat"):
            enriched_pains.append(pain)
            continue
        
        # Search for statistics about this pain
        query = f'"{pain_text}" statistics data {idea} India 2024 2025'
        results = search_indian_sources(query, max_results=3)
        
        if results:
            # Add sources to the pain point
            sources = [r.get("url", "") for r in results if r.get("url")]
            pain["sources"] = sources
            pain["search_results"] = [
                {"url": r.get("url"), "snippet": r.get("content", "")[:300]}
                for r in results
            ]
        
        enriched_pains.append(pain)
    
    # Use LLM to extract statistics from search results
    llm = get_research_llm()
    
    messages = [
        SystemMessage(content=CRITIC_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}
ITERATION: {iteration + 1} of {max_iterations}

PAIN POINTS TO VERIFY:
{json.dumps(enriched_pains, indent=2)}

For each pain point, extract:
1. A specific statistic (%, ₹ amount, time wasted)
2. The source of the statistic
3. The year of the data

If you cannot find statistics for a pain point, reject it.
Return your response as valid JSON matching the output format specified.
""")
    ]
    
    response = llm.invoke(messages)
    
    # Parse LLM response
    try:
        content = response.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(content[json_start:json_end])
            verified_pains = parsed.get("verified_pains", [])
            rejected_pains = parsed.get("rejected_pains", [])
            llm_verified = parsed.get("is_verified", False)
            llm_feedback = parsed.get("feedback", "")
        else:
            verified_pains = []
            rejected_pains = []
            llm_verified = False
            llm_feedback = "Failed to parse verification results"
    except json.JSONDecodeError:
        verified_pains = []
        rejected_pains = []
        llm_verified = False
        llm_feedback = "Failed to parse LLM response"
    
    # Apply domain trust scoring to verified pains
    scored_pains = score_pain_points(verified_pains)
    
    # Filter to only truly verified pains (meet our threshold)
    truly_verified = [p for p in scored_pains if p.get("is_verified", False)]
    
    # Determine if we have enough verified pains (at least 3)
    is_verified = len(truly_verified) >= 3
    
    # Generate feedback if not verified
    if not is_verified:
        feedback = get_verification_feedback(scored_pains)
        if iteration + 1 >= max_iterations:
            feedback += "\n\n⚠️ Maximum iterations reached. Proceeding with available data."
            is_verified = True  # Force proceed
    else:
        feedback = ""
    
    return {
        "verified_pains": truly_verified,
        "is_verified": is_verified,
        "critic_feedback": feedback or llm_feedback,
        "iteration_count": iteration + 1,
        "rejected_pains": rejected_pains
    }


def should_loop_to_strategist(state: MarketState) -> bool:
    """
    Conditional edge function: Should we loop back to Strategist?
    
    Returns True if:
    - Not verified AND
    - Haven't exceeded max iterations
    """
    is_verified = state.get("is_verified", False)
    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    return not is_verified and iteration < max_iterations
