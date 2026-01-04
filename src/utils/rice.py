"""
RICE Feature Scoring System for the Innovator agent.

RICE is a prioritization framework used by product teams to objectively
rank features based on:
    - Reach: How many users will this affect? (number)
    - Impact: How much will it affect them? (1-3 scale)
    - Confidence: How sure are we about reach/impact? (0-1)
    - Effort: How much work to build? (person-weeks)

Formula:
    RICE Score = (Reach × Impact × Confidence) / Effort

Higher score = higher priority.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FeatureScore:
    """A feature with its RICE score calculated."""
    name: str
    reach: int
    impact: int          # 1, 2, or 3
    confidence: float    # 0.0 to 1.0
    effort: int          # person-weeks
    rice_score: float
    priority_rank: int = 0


def calculate_rice_score(
    reach: int,
    impact: int,
    confidence: float,
    effort: int
) -> float:
    """
    Calculate the RICE score for a single feature.
    
    Args:
        reach: Number of users affected per quarter
        impact: 1 (minimal), 2 (medium), 3 (massive)
        confidence: 0.0 (pure guess) to 1.0 (data-backed)
        effort: Person-weeks to build
    
    Returns:
        RICE score (higher = more valuable)
    
    Example:
        Reach = 10,000 users
        Impact = 3 (massive)
        Confidence = 0.8 (fairly confident)
        Effort = 4 weeks
        
        Score = (10000 × 3 × 0.8) / 4 = 6,000
    """
    if effort <= 0:
        return 0.0
    
    return (reach * impact * confidence) / effort


def score_features(features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calculate RICE scores for a list of features and sort by priority.
    
    Expected input format:
        {
            "name": str,
            "description": str,
            "reach": int,
            "impact": int (1-3),
            "confidence": float (0-1),
            "effort": int (person-weeks),
            ...other fields
        }
    
    Returns:
        Same list with 'rice_score' and 'priority_rank' added, sorted by score.
    """
    scored = []
    
    for feature in features:
        rice_score = calculate_rice_score(
            reach=feature.get('reach', 0),
            impact=feature.get('impact', 1),
            confidence=feature.get('confidence', 0.5),
            effort=feature.get('effort', 1)
        )
        
        scored.append({
            **feature,
            'rice_score': round(rice_score, 2)
        })
    
    # Sort by RICE score descending
    scored.sort(key=lambda x: x['rice_score'], reverse=True)
    
    # Add priority rank
    for i, feature in enumerate(scored, 1):
        feature['priority_rank'] = i
    
    return scored


def get_top_features(features: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top N features by RICE score.
    
    Useful for the executive summary where we only show the most impactful features.
    """
    scored = score_features(features)
    return scored[:n]


def generate_prioritization_summary(features: List[Dict[str, Any]]) -> str:
    """
    Generate a human-readable summary of feature prioritization.
    """
    scored = score_features(features)
    
    lines = [
        "## Feature Prioritization (by RICE Score)\n",
        "| Rank | Feature | RICE Score | Reach | Impact | Effort |",
        "|------|---------|------------|-------|--------|--------|"
    ]
    
    for f in scored[:10]:  # Top 10
        lines.append(
            f"| {f['priority_rank']} | {f['name'][:30]} | {f['rice_score']:,.0f} | "
            f"{f['reach']:,} | {f['impact']} | {f['effort']}w |"
        )
    
    return "\n".join(lines)


def validate_rice_inputs(features: List[Dict[str, Any]]) -> List[str]:
    """
    Validate that features have proper RICE parameters.
    
    Returns a list of validation errors.
    """
    errors = []
    
    for i, feature in enumerate(features):
        name = feature.get('name', f'Feature {i+1}')
        
        if not feature.get('reach'):
            errors.append(f"'{name}': Missing 'reach' (number of users affected)")
        
        impact = feature.get('impact', 0)
        if impact not in [1, 2, 3]:
            errors.append(f"'{name}': 'impact' must be 1, 2, or 3 (got {impact})")
        
        confidence = feature.get('confidence', -1)
        if not (0 <= confidence <= 1):
            errors.append(f"'{name}': 'confidence' must be 0-1 (got {confidence})")
        
        effort = feature.get('effort', 0)
        if effort <= 0:
            errors.append(f"'{name}': 'effort' must be > 0 person-weeks (got {effort})")
    
    return errors


def categorize_features(features: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize features into priority buckets.
    
    Returns:
        {
            "quick_wins": High score, low effort
            "big_bets": High score, high effort
            "maybes": Medium score
            "ice_box": Low score (deprioritize)
        }
    """
    scored = score_features(features)
    
    buckets = {
        "quick_wins": [],   # Score > 5000, Effort < 4 weeks
        "big_bets": [],     # Score > 5000, Effort >= 4 weeks
        "maybes": [],       # Score 1000-5000
        "ice_box": []       # Score < 1000
    }
    
    for f in scored:
        score = f['rice_score']
        effort = f.get('effort', 999)
        
        if score > 5000:
            if effort < 4:
                buckets["quick_wins"].append(f)
            else:
                buckets["big_bets"].append(f)
        elif score > 1000:
            buckets["maybes"].append(f)
        else:
            buckets["ice_box"].append(f)
    
    return buckets
