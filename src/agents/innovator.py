"""
Agent 6: The Innovator

Role: Propose Delta-4 features with RICE scoring.
Uses: LLM for ideation + Python RICE Calculator

The Innovator:
1. Takes pains, personas, and competitor gaps as input
2. Proposes 25 features that deliver 10x improvement
3. Estimates RICE parameters for each feature
4. Python calculates exact RICE scores and ranks features
"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import MarketState
from src.config.prompts import INNOVATOR_PROMPT
from src.utils.llm import get_llm
from src.utils.rice import score_features, validate_rice_inputs, categorize_features


def run_innovator(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Innovator agent.
    
    Inputs from state:
        - verified_pains: Problems to solve
        - competitor_table: Gaps to exploit
        - personas: Users to target
        - market_gaps: Strategic opportunities
        - auditor_feedback: If looping, what needs to change
    
    Outputs to state:
        - feature_list: 25 features with RICE scores
        - feature_categories: Quick wins, big bets, etc.
    """
    idea = state.get("raw_idea", "")
    verified_pains = state.get("verified_pains", [])
    competitors = state.get("competitor_table", [])
    personas = state.get("personas", [])
    market_gaps = state.get("market_gaps", [])
    auditor_feedback = state.get("auditor_feedback", "")
    
    # Build comprehensive context
    pain_list = "\n".join([
        f"- PAIN: {p.get('pain', '')}"
        for p in verified_pains
    ])
    
    lack_list = "\n".join([
        f"- {c.get('name', 'Unknown')} lacks: {c.get('lack', 'N/A')}"
        for c in competitors
    ])
    
    gap_list = "\n".join([f"- {gap}" for gap in market_gaps])
    
    persona_list = "\n".join([
        f"- {p.get('name', '')} ({p.get('segment', '')})"
        for p in personas
    ])
    
    # Add feedback context if we're in a loop
    feedback_context = ""
    if auditor_feedback:
        feedback_context = f"""
⚠️ PREVIOUS FEEDBACK FROM AUDITOR:
{auditor_feedback}

Please simplify features or adjust scope to improve financial viability.
"""
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content=INNOVATOR_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}

VERIFIED PAINS TO SOLVE:
{pain_list}

COMPETITOR LACKS TO EXPLOIT:
{lack_list}

MARKET GAPS IDENTIFIED:
{gap_list}

PERSONAS TO TARGET:
{persona_list}
{feedback_context}

Propose 25 features that deliver Delta-4 (10x) improvements.
Each feature MUST:
1. Link to a specific pain point
2. Link to a competitor lack
3. Target a specific persona
4. Have RICE parameters (reach, impact 1-3, confidence 0-1, effort in person-weeks)

Think carefully about effort estimates - be realistic, not optimistic.

Return your response as valid JSON matching the output format specified.
""")
    ]
    
    response = llm.invoke(messages)
    
    # Parse response
    try:
        content = response.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(content[json_start:json_end])
            features = parsed.get("features", [])
        else:
            features = []
    except json.JSONDecodeError:
        features = []
    
    # Validate RICE inputs
    validation_errors = validate_rice_inputs(features)
    
    # Calculate RICE scores using our Python module
    scored_features = score_features(features)
    
    # Categorize into buckets
    categories = categorize_features(scored_features)
    
    return {
        "feature_list": scored_features,
        "feature_categories": {
            "quick_wins": len(categories.get("quick_wins", [])),
            "big_bets": len(categories.get("big_bets", [])),
            "maybes": len(categories.get("maybes", [])),
            "ice_box": len(categories.get("ice_box", []))
        },
        "feature_validation_errors": validation_errors,
        "top_5_features": scored_features[:5] if scored_features else []
    }
