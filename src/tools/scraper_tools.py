"""
Web Scraping Tools for Competitor Intelligence.

These tools allow agents to autonomously scrape competitor websites
without needing separate LLM calls.
"""

from typing import Dict, Any
from langchain_core.tools import tool
from src.utils.scraper import analyze_competitor, detect_dark_patterns


@tool
def scrape_competitor_website(url: str) -> Dict[str, Any]:
    """
    Scrape a competitor's website to extract pricing, features, and detect dark patterns.
    
    Args:
        url: The competitor's website URL (must start with http:// or https://)
    
    Returns:
        Dictionary containing pricing tiers, feature list, dark patterns found, and metadata.
    """
    try:
        result = analyze_competitor(url)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "url": url,
            "success": False
        }


@tool
def detect_competitor_dark_patterns(url: str) -> Dict[str, Any]:
    """
    Scan a competitor's website specifically for dark patterns and deceptive UX.
    
    Args:
        url: The competitor's website URL
    
    Returns:
        Dictionary with dark_patterns_found list, suspicion_score (0-10), and details.
    """
    try:
        result = detect_dark_patterns(url)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "url": url,
            "dark_patterns_found": [],
            "suspicion_score": 0
        }
