"""
Search Tool Configuration.

Wraps Tavily for market research purposes with Indian domain priorities.
"""

import os
from typing import List, Dict, Any, Optional
from langchain_community.tools.tavily_search import TavilySearchResults
from src.config.settings import TAVILY_API_KEY


def get_search_tool(max_results: int = 5) -> TavilySearchResults:
    """
    Returns a configured Tavily search tool.
    """
    if not TAVILY_API_KEY:
        raise ValueError(
            "TAVILY_API_KEY not found. Please set it in your .env file."
        )
    
    # Set the API key in environment (Tavily client reads from here)
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    
    return TavilySearchResults(
        max_results=max_results,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=False,
    )


def search_with_domains(
    query: str,
    domains: Optional[List[str]] = None,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Perform a search with optional domain filtering.
    
    Args:
        query: The search query
        domains: List of domains to prioritize (e.g., ["reddit.com", "inc42.com"])
        max_results: Maximum number of results
    
    Returns:
        List of search results with url, content, etc.
    """
    tool = get_search_tool(max_results)
    
    # If domains specified, add site filters to query
    if domains:
        site_filter = " OR ".join([f"site:{d}" for d in domains])
        query = f"({site_filter}) {query}"
    
    try:
        results = tool.invoke(query)
        return results if isinstance(results, list) else []
    except Exception as e:
        print(f"Search error: {e}")
        return []


def search_indian_sources(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search prioritizing Indian news and startup sources.
    """
    indian_domains = [
        "inc42.com",
        "yourstory.com",
        "economictimes.com",
        "livemint.com",
        "moneycontrol.com",
        "entrackr.com",
    ]
    return search_with_domains(query, indian_domains, max_results)


def search_community_sources(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search community platforms for user complaints and discussions.
    """
    community_domains = [
        "reddit.com",
        "twitter.com",
        "quora.com",
    ]
    return search_with_domains(query, community_domains, max_results)


def build_search_queries(idea: str, region: str = "India") -> List[str]:
    """
    Generate effective search queries for market research.
    
    Returns multiple query variations to maximize coverage.
    """
    queries = [
        f'"{idea}" problems {region}',
        f'"{idea}" complaints {region}',
        f'"{idea}" alternatives {region}',
        f'"{idea}" vs competitors {region}',
        f'"{idea}" market size {region} 2025',
        f'"{idea}" user reviews',
        f'"I switched from" "{idea}"',
        f'"problem with" "{idea}"',
    ]
    return queries
