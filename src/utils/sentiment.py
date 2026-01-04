"""
Sentiment Analysis Engine using VADER.

VADER (Valence Aware Dictionary and sEntiment Reasoner) is specifically
designed for social media text, making it perfect for analyzing Reddit
and Twitter complaints.

Why VADER over LLM sentiment?
1. Deterministic: Same input always gives same output
2. Fast: No API call needed
3. Handles slang, emojis, and internet-speak well
4. Returns a precise numerical score we can threshold on
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any
from src.config.settings import MAX_SENTIMENT_FOR_PAIN


# Initialize once at module load (singleton pattern)
_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Analyze the sentiment of a single piece of text.
    
    Returns:
        {
            'neg': 0.0-1.0,    # Proportion of negative sentiment
            'neu': 0.0-1.0,    # Proportion of neutral sentiment
            'pos': 0.0-1.0,    # Proportion of positive sentiment
            'compound': -1 to 1 # Overall sentiment score
        }
    
    The 'compound' score is what we care about most:
    - < -0.5: Very negative (strong pain signal)
    - -0.5 to -0.3: Moderately negative (potential pain)
    - -0.3 to 0.3: Neutral
    - > 0.3: Positive (not a pain point)
    """
    return _analyzer.polarity_scores(text)


def get_rage_score(text: str) -> float:
    """
    Returns the compound sentiment score.
    Lower is angrier. Range: -1 (pure rage) to +1 (pure joy).
    """
    scores = analyze_sentiment(text)
    return scores['compound']


def is_genuine_pain(text: str) -> bool:
    """
    Determines if a user complaint represents genuine pain.
    
    We filter out:
    - Mild inconveniences (slightly negative sentiment)
    - Neutral observations
    - Positive experiences
    
    Only strongly negative sentiment passes the filter.
    """
    rage_score = get_rage_score(text)
    return rage_score < MAX_SENTIMENT_FOR_PAIN


def analyze_pain_points(pain_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Batch analyze pain points and add sentiment scores.
    
    Args:
        pain_points: List of dicts with 'pain' or 'raw_quote' keys
    
    Returns:
        Same list with 'sentiment_score' and 'is_genuine_pain' added
    """
    analyzed = []
    
    for point in pain_points:
        # Try to get the most relevant text for sentiment
        text = point.get('raw_quote') or point.get('pain', '')
        
        if not text:
            continue
        
        sentiment = get_rage_score(text)
        
        analyzed.append({
            **point,
            'sentiment_score': sentiment,
            'is_genuine_pain': sentiment < MAX_SENTIMENT_FOR_PAIN,
        })
    
    return analyzed


def filter_genuine_pains(pain_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter to only include pain points with genuine negative sentiment.
    
    This is the key function that prevents "mild inconveniences" from
    making it into the final report.
    """
    analyzed = analyze_pain_points(pain_points)
    return [p for p in analyzed if p.get('is_genuine_pain', False)]
