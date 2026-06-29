"""
Tool Registry for LangGraph Agents.

Centralized management of which tools are available to which agents.
"""

from typing import List
from langchain_core.tools import BaseTool

# Tools exports (legacy functions)
from .search import (
    get_search_tool,
    search_with_domains,
    build_search_queries
)

# LangChain Tools
from .search import search_indian_sources, search_community_sources
from .scraper_tools import scrape_competitor_website, detect_competitor_dark_patterns
from .financial_tools import calculate_unit_economics, run_financial_model


# Define tool sets for each agent
STRATEGIST_TOOLS = [
    search_community_sources,  # For finding user complaints
    search_indian_sources,     # For finding market data
]

CRITIC_TOOLS = [
    search_indian_sources,     # For verifying statistics
]

INFILTRATOR_TOOLS = [
    search_indian_sources,     # For finding competitors
    scrape_competitor_website, # For extracting competitor data
    detect_competitor_dark_patterns,  # For UX analysis
]

AUDITOR_TOOLS = [
    calculate_unit_economics,  # For quick LTV/CAC calculations
    run_financial_model,       # For full financial projections
]

# All tools combined
ALL_TOOLS = [
    search_indian_sources,
    search_community_sources,
    scrape_competitor_website,
    detect_competitor_dark_patterns,
    calculate_unit_economics,
    run_financial_model,
]


def get_tools_for_agent(agent_name: str) -> List[BaseTool]:
    """
    Get the list of tools available to a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., "strategist", "critic")
    
    Returns:
        List of LangChain tools that the agent can use.
    """
    tool_registry = {
        "strategist": STRATEGIST_TOOLS,
        "critic": CRITIC_TOOLS,
        "infiltrator": INFILTRATOR_TOOLS,
        "auditor": AUDITOR_TOOLS,
    }
    
    return tool_registry.get(agent_name.lower(), [])


def get_all_tools() -> List[BaseTool]:
    """
    Get all available tools for the workflow.
    
    Returns:
        List of all tools in the system.
    """
    return ALL_TOOLS

