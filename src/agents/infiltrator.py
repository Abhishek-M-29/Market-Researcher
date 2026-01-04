"""
Agent 3: The Infiltrator

Role: Competitive intelligence and mystery shopping.
Uses: BeautifulSoup Scraper + LLM Analysis

The Infiltrator:
1. Identifies competitors from search results
2. Actually visits their websites
3. Extracts pricing and detects dark patterns
4. Builds a preliminary competitor profile
"""

import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import MarketState
from src.config.prompts import INFILTRATOR_PROMPT
from src.utils.llm import get_llm
from src.utils.scraper import analyze_competitor, batch_analyze_competitors
from src.tools.search import search_indian_sources


def run_infiltrator(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Infiltrator agent.
    
    Inputs from state:
        - raw_idea: The idea to find competitors for
        - verified_pains: Gives context on what gaps to look for
    
    Outputs to state:
        - competitor_table: Structured competitor intelligence
    """
    idea = state.get("raw_idea", "")
    region = state.get("target_region", "India")
    verified_pains = state.get("verified_pains", [])
    
    # Step 1: Find competitors through search
    competitor_query = f'"{idea}" competitors alternatives {region}'
    search_results = search_indian_sources(competitor_query, max_results=5)
    
    # Also search for specific competitor names
    direct_query = f'{idea} top companies {region} 2025'
    direct_results = search_indian_sources(direct_query, max_results=5)
    
    all_results = search_results + direct_results
    
    # Step 2: Use LLM to extract competitor URLs from search results
    llm = get_llm()
    
    extract_messages = [
        SystemMessage(content="Extract competitor company names and their website URLs from the search results. Return as JSON: {\"competitors\": [{\"name\": str, \"url\": str}]}"),
        HumanMessage(content=f"""
IDEA: {idea}
REGION: {region}

SEARCH RESULTS:
{json.dumps([{"url": r.get("url"), "content": r.get("content", "")[:300]} for r in all_results], indent=2)}

Extract the main competitor companies and their URLs.
Focus on Indian competitors or those with strong India presence.
""")
    ]
    
    extract_response = llm.invoke(extract_messages)
    
    # Parse competitor URLs
    try:
        content = extract_response.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(content[json_start:json_end])
            competitor_list = parsed.get("competitors", [])
        else:
            competitor_list = []
    except json.JSONDecodeError:
        competitor_list = []
    
    # Step 3: Actually scrape competitor websites
    scraped_data = []
    for comp in competitor_list[:5]:  # Limit to 5 competitors
        url = comp.get("url", "")
        if url and url.startswith("http"):
            try:
                scraped = analyze_competitor(url)
                scraped["name"] = comp.get("name", "Unknown")
                scraped_data.append(scraped)
            except Exception as e:
                scraped_data.append({
                    "name": comp.get("name", "Unknown"),
                    "url": url,
                    "error": str(e)
                })
    
    # Step 4: Use LLM to synthesize findings
    pain_context = "\n".join([f"- {p.get('pain', '')}" for p in verified_pains])
    
    messages = [
        SystemMessage(content=INFILTRATOR_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}
REGION: {region}

VERIFIED USER PAINS:
{pain_context}

SCRAPED COMPETITOR DATA:
{json.dumps(scraped_data, indent=2)}

SEARCH CONTEXT:
{json.dumps([{"url": r.get("url"), "content": r.get("content", "")[:200]} for r in all_results[:5]], indent=2)}

Analyze these competitors. For each one, identify:
1. Their pricing strategy
2. Dark patterns detected
3. Technical gaps (especially compared to user pains)
4. What they do well and poorly

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
            competitors = parsed.get("competitors", [])
        else:
            competitors = []
    except json.JSONDecodeError:
        competitors = []
    
    # Enrich with scraped data
    for comp in competitors:
        # Find matching scraped data
        for scraped in scraped_data:
            if scraped.get("name", "").lower() == comp.get("name", "").lower():
                comp["scraped_pricing"] = scraped.get("pricing", {})
                comp["scraped_dark_patterns"] = scraped.get("dark_patterns", {})
                break
    
    return {
        "competitor_table": competitors,
        "raw_scraped_data": scraped_data
    }
