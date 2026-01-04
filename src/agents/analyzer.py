"""
Agent 5: The Market Analyzer

Role: Synthesize competitor data into a strategic matrix.
Uses: LLM for synthesis + structured output

The Analyzer:
1. Takes competitor data from Infiltrator
2. Builds a comprehensive matrix
3. Identifies market gaps and positioning opportunities
"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import MarketState
from src.config.prompts import ANALYZER_PROMPT
from src.utils.llm import get_llm


def run_analyzer(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Analyzer agent.
    
    Inputs from state:
        - competitor_table: Raw competitor intel from Infiltrator
        - verified_pains: Context on what users need
        - personas: Context on who we're targeting
    
    Outputs to state:
        - competitor_table: Enriched with Lag/Lack/Gap analysis
        - market_gaps: List of identified opportunities
        - recommended_positioning: Strategic recommendation
    """
    idea = state.get("raw_idea", "")
    competitors = state.get("competitor_table", [])
    verified_pains = state.get("verified_pains", [])
    personas = state.get("personas", [])
    
    # Build context
    pain_context = "\n".join([
        f"- {p.get('pain', '')}"
        for p in verified_pains
    ])
    
    persona_needs = "\n".join([
        f"- {p.get('name', 'Unknown')} ({p.get('segment', '')}): {p.get('current_workaround', 'N/A')}"
        for p in personas[:5]  # Top 5 personas
    ])
    
    competitor_context = json.dumps(competitors, indent=2)
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content=ANALYZER_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}

VERIFIED USER PAINS:
{pain_context}

KEY PERSONA WORKAROUNDS:
{persona_needs}

COMPETITOR DATA:
{competitor_context}

Analyze the competitive landscape:
1. For each competitor, identify their Lag (slow to innovate), Lack (missing features), and Gap (our opportunity)
2. Map which user pains each competitor solves and which they leave unsolved
3. Recommend our strategic positioning

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
            enriched_matrix = parsed.get("competitor_matrix", [])
            market_gaps = parsed.get("market_gaps", [])
            positioning = parsed.get("recommended_positioning", "")
        else:
            enriched_matrix = competitors
            market_gaps = []
            positioning = ""
    except json.JSONDecodeError:
        enriched_matrix = competitors
        market_gaps = []
        positioning = ""
    
    # Merge enriched data with original competitor data
    for enriched in enriched_matrix:
        for original in competitors:
            if enriched.get("name", "").lower() == original.get("name", "").lower():
                original.update(enriched)
    
    return {
        "competitor_table": competitors if competitors else enriched_matrix,
        "market_gaps": market_gaps,
        "recommended_positioning": positioning
    }
