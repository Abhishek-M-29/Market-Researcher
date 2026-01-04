"""
Domain Trust Scoring System for the Critic agent.

This module provides deterministic scoring of sources based on domain authority.
It removes the subjectivity of asking an LLM "is this a reliable source?"

The scoring logic:
1. Extract domain from URL
2. Look up domain in our trust database
3. Return a numerical score (0-10)

Higher scores = more trustworthy
"""

from urllib.parse import urlparse
from typing import List, Dict, Any, Optional
from src.config.settings import DOMAIN_TRUST_SCORES, MIN_CONFIDENCE_THRESHOLD


def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.
    
    Examples:
        "https://www.inc42.com/article/123" -> "inc42.com"
        "https://economictimes.com/news" -> "economictimes.com"
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except Exception:
        return ""


def get_domain_trust_score(url: str) -> int:
    """
    Get the trust score for a given URL based on its domain.
    
    Returns:
        Integer score from 0-10
    """
    domain = extract_domain(url)
    
    if not domain:
        return 0
    
    # Check for exact domain match
    if domain in DOMAIN_TRUST_SCORES:
        return DOMAIN_TRUST_SCORES[domain]
    
    # Check for TLD matches (e.g., ".gov.in")
    for tld, score in DOMAIN_TRUST_SCORES.items():
        if tld.startswith('.') and domain.endswith(tld):
            return score
    
    # Check if domain contains any trusted domain
    for trusted_domain, score in DOMAIN_TRUST_SCORES.items():
        if not trusted_domain.startswith('.') and trusted_domain in domain:
            return score
    
    # Default score for unknown domains
    return DOMAIN_TRUST_SCORES.get('default', 2)


def calculate_claim_confidence(
    sources: List[str],
    has_statistic: bool = False,
    year: Optional[int] = None
) -> int:
    """
    Calculate the overall confidence score for a claim based on its sources.
    
    Scoring formula:
        Base Score = Sum of domain trust scores
        + 5 bonus points if there's a numerical statistic
        + 3 bonus points if data is from 2024-2026
    
    Args:
        sources: List of URLs supporting the claim
        has_statistic: Whether the claim includes numerical evidence
        year: The year of the data (if known)
    
    Returns:
        Confidence score (higher = more reliable)
    """
    score = 0
    
    # Sum up domain trust scores
    for source in sources:
        score += get_domain_trust_score(source)
    
    # Bonus for statistical evidence
    if has_statistic:
        score += 5
    
    # Bonus for recent data
    if year and year >= 2024:
        score += 3
    
    return score


def is_claim_verified(
    sources: List[str],
    has_statistic: bool = False,
    year: Optional[int] = None
) -> bool:
    """
    Determine if a claim meets the minimum verification threshold.
    
    This is the gate-keeping function used by the Critic agent.
    """
    confidence = calculate_claim_confidence(sources, has_statistic, year)
    return confidence >= MIN_CONFIDENCE_THRESHOLD


def score_pain_points(pain_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add confidence scores to a list of pain points.
    
    Expected input format:
        {
            "pain": str,
            "stat": str (optional),
            "source": str or list of str,
            "year": int (optional)
        }
    """
    scored = []
    
    for point in pain_points:
        # Handle both single source and list of sources
        sources = point.get('source', [])
        if isinstance(sources, str):
            sources = [sources]
        
        has_stat = bool(point.get('stat'))
        year = point.get('year')
        
        confidence = calculate_claim_confidence(sources, has_stat, year)
        
        scored.append({
            **point,
            'confidence_score': confidence,
            'is_verified': confidence >= MIN_CONFIDENCE_THRESHOLD,
            'domain_scores': {
                extract_domain(s): get_domain_trust_score(s) 
                for s in sources
            }
        })
    
    return scored


def get_verification_feedback(pain_points: List[Dict[str, Any]]) -> str:
    """
    Generate feedback explaining why verification failed.
    
    This feedback is passed back to the Strategist for refinement.
    """
    unverified = [p for p in pain_points if not p.get('is_verified', False)]
    
    if not unverified:
        return "All pain points are verified."
    
    feedback_lines = ["The following pain points need stronger evidence:\n"]
    
    for point in unverified:
        pain = point.get('pain', 'Unknown pain')
        score = point.get('confidence_score', 0)
        needed = MIN_CONFIDENCE_THRESHOLD - score
        
        feedback_lines.append(
            f"- '{pain[:50]}...': Score {score}/{MIN_CONFIDENCE_THRESHOLD}. "
            f"Need {needed} more points. Try finding .gov.in or major news sources."
        )
    
    return "\n".join(feedback_lines)
