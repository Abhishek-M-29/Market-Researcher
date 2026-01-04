"""
Agent 4: The Anthropologist

Role: Create detailed user personas using the India 1, 2, 3 framework.
Uses: Pure LLM creativity based on verified research

The Anthropologist:
1. Takes verified pains and competitor insights
2. Creates 10 detailed personas across India segments
3. Assigns trust deficit scores and language preferences
"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import MarketState
from src.config.prompts import ANTHROPOLOGIST_PROMPT
from src.config.settings import INDIA_SEGMENTS
from src.utils.llm import get_analysis_llm


def run_anthropologist(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Anthropologist agent.
    
    Inputs from state:
        - raw_idea: The product idea
        - verified_pains: What problems we're solving
        - competitor_table: Who we're competing with
    
    Outputs to state:
        - personas: 10 detailed user personas
    """
    idea = state.get("raw_idea", "")
    verified_pains = state.get("verified_pains", [])
    competitors = state.get("competitor_table", [])
    
    # Build context for LLM
    pain_context = "\n".join([
        f"- {p.get('pain', '')}: {p.get('stat', 'No stat')}"
        for p in verified_pains
    ])
    
    competitor_context = "\n".join([
        f"- {c.get('name', 'Unknown')}: Best at {c.get('best_at', 'N/A')}, Lacks {c.get('lack', 'N/A')}"
        for c in competitors
    ])
    
    # India segment descriptions
    segment_context = "\n".join([
        f"- {name}: {info['description']} ({info['population_range']}, {info['income']})"
        for name, info in INDIA_SEGMENTS.items()
    ])
    
    llm = get_analysis_llm()
    
    messages = [
        SystemMessage(content=ANTHROPOLOGIST_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}

VERIFIED PAINS WE'RE SOLVING:
{pain_context}

COMPETITOR LANDSCAPE:
{competitor_context}

INDIA SEGMENT DEFINITIONS:
{segment_context}

Create 10 detailed personas:
- 3-4 from India 1 (metros, high income, tech-savvy)
- 3-4 from India 2 (tier 2, middle class, UPI-native)
- 2-3 from India 3 (tier 3+, offline-to-online transition)

For each persona, think deeply about:
1. Their daily life and frustrations
2. How they currently solve this problem (workaround)
3. What would make them trust and adopt a new solution
4. Their comfort with technology and language preferences

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
            personas = parsed.get("personas", [])
        else:
            personas = []
    except json.JSONDecodeError:
        personas = []
    
    # Ensure we have segment distribution
    segment_counts = {"India 1": 0, "India 2": 0, "India 3": 0}
    for persona in personas:
        segment = persona.get("segment", "")
        if segment in segment_counts:
            segment_counts[segment] += 1
    
    return {
        "personas": personas,
        "persona_distribution": segment_counts
    }
