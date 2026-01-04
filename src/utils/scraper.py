"""
Web Scraper for Competitor Intelligence.

This module provides real web scraping capabilities for the Infiltrator agent.
It extracts actual data from competitor websites instead of relying on
LLM knowledge (which may be outdated).

Features:
1. Pricing page extraction
2. Dark pattern detection
3. Keyword density analysis
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import re
from src.config.settings import DARK_PATTERN_KEYWORDS


# Standard headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def fetch_page(url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
    """
    Fetch a webpage and return a BeautifulSoup object.
    
    Returns None if the request fails.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def extract_text(soup: BeautifulSoup) -> str:
    """
    Extract all visible text from a page.
    """
    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    return soup.get_text(separator=' ', strip=True)


def detect_dark_patterns(url: str) -> Dict[str, Any]:
    """
    Scan a webpage for dark pattern indicators.
    
    Returns:
        {
            "url": str,
            "dark_patterns_found": [str],
            "suspicion_score": int (0-10),
            "raw_matches": {keyword: count}
        }
    """
    soup = fetch_page(url)
    
    result = {
        "url": url,
        "dark_patterns_found": [],
        "suspicion_score": 0,
        "raw_matches": {}
    }
    
    if not soup:
        result["error"] = "Failed to fetch page"
        return result
    
    text = extract_text(soup).lower()
    
    # Check for each dark pattern keyword
    for keyword in DARK_PATTERN_KEYWORDS:
        count = text.count(keyword.lower())
        if count > 0:
            result["raw_matches"][keyword] = count
            result["dark_patterns_found"].append(keyword)
            result["suspicion_score"] += min(count, 3)  # Cap at 3 per keyword
    
    # Cap suspicion score at 10
    result["suspicion_score"] = min(result["suspicion_score"], 10)
    
    return result


def extract_pricing_info(url: str) -> Dict[str, Any]:
    """
    Attempt to extract pricing information from a webpage.
    
    Looks for:
    - Currency symbols (₹, $, Rs)
    - Common pricing patterns (/month, /year, /mo)
    - Pricing tables
    
    Returns:
        {
            "url": str,
            "prices_found": [str],
            "pricing_tiers": [str],
            "has_free_tier": bool
        }
    """
    soup = fetch_page(url)
    
    result = {
        "url": url,
        "prices_found": [],
        "pricing_tiers": [],
        "has_free_tier": False,
        "has_trial": False
    }
    
    if not soup:
        result["error"] = "Failed to fetch page"
        return result
    
    text = extract_text(soup)
    
    # Look for Indian Rupee prices
    rupee_pattern = r'₹\s*[\d,]+(?:\.\d{2})?(?:\s*(?:/|per)\s*(?:mo|month|year|yr))?'
    rupee_matches = re.findall(rupee_pattern, text)
    result["prices_found"].extend(rupee_matches)
    
    # Look for "Rs" format
    rs_pattern = r'Rs\.?\s*[\d,]+(?:\.\d{2})?(?:\s*(?:/|per)\s*(?:mo|month|year|yr))?'
    rs_matches = re.findall(rs_pattern, text, re.IGNORECASE)
    result["prices_found"].extend(rs_matches)
    
    # Look for dollar prices (for SaaS)
    dollar_pattern = r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:/|per)\s*(?:mo|month|year|yr))?'
    dollar_matches = re.findall(dollar_pattern, text)
    result["prices_found"].extend(dollar_matches)
    
    # Check for free tier
    if re.search(r'\bfree\s*(?:plan|tier|forever)\b', text, re.IGNORECASE):
        result["has_free_tier"] = True
    
    # Check for trial
    if re.search(r'\b(?:free\s*)?trial\b', text, re.IGNORECASE):
        result["has_trial"] = True
    
    # Look for tier names
    tier_patterns = [
        r'\b(basic|starter|free|pro|professional|business|enterprise|premium|plus)\s*(?:plan|tier)?\b',
    ]
    for pattern in tier_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        result["pricing_tiers"].extend(set(m.capitalize() for m in matches))
    
    # Deduplicate
    result["prices_found"] = list(set(result["prices_found"]))[:10]
    result["pricing_tiers"] = list(set(result["pricing_tiers"]))
    
    return result


def analyze_competitor(url: str) -> Dict[str, Any]:
    """
    Perform a comprehensive analysis of a competitor's website.
    
    Combines dark pattern detection, pricing extraction, and general intel.
    """
    # Get the main page
    soup = fetch_page(url)
    
    result = {
        "url": url,
        "accessible": soup is not None,
        "title": "",
        "description": "",
        "dark_patterns": {},
        "pricing": {},
        "features_mentioned": []
    }
    
    if not soup:
        return result
    
    # Extract basic info
    title_tag = soup.find('title')
    result["title"] = title_tag.get_text(strip=True) if title_tag else ""
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        result["description"] = meta_desc.get('content', '')
    
    # Try to find pricing page
    pricing_links = soup.find_all('a', href=re.compile(r'pricing|plans', re.I))
    if pricing_links:
        pricing_url = urljoin(url, pricing_links[0].get('href', ''))
        result["pricing"] = extract_pricing_info(pricing_url)
    else:
        # Try common pricing URLs
        for path in ['/pricing', '/plans', '/pricing.html']:
            pricing_url = urljoin(url, path)
            pricing_result = extract_pricing_info(pricing_url)
            if pricing_result.get("prices_found"):
                result["pricing"] = pricing_result
                break
    
    # Dark pattern analysis on main page
    result["dark_patterns"] = detect_dark_patterns(url)
    
    return result


def batch_analyze_competitors(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze multiple competitor URLs.
    """
    results = []
    for url in urls:
        result = analyze_competitor(url)
        results.append(result)
    return results
