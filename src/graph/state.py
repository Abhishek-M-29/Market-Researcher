"""
MarketState: The Single Source of Truth for the entire research pipeline.

This TypedDict flows through every agent in the graph. Each agent reads from it,
processes data, and writes back to it. The control flags (is_verified, is_financially_viable)
determine whether the graph loops back or proceeds forward.
"""

from typing import TypedDict, List, Optional, Dict, Any


class VerifiedPain(TypedDict):
    """A pain point that has been verified with a statistic and source."""
    pain: str           # The actual problem users face
    stat: str           # The numerical evidence (e.g., "67% of users report...")
    source: str         # Where this data came from (URL or publication name)
    year: int           # How recent is this data
    sentiment_score: float  # VADER polarity score (-1 to 1)


class Competitor(TypedDict):
    """Structured competitive intelligence on a single competitor."""
    name: str
    url: str
    features: List[str]
    best_at: str        # What they do exceptionally well
    lag: str            # Where they are slow to innovate
    lack: str           # What they are missing entirely
    gap: str            # The opportunity we can exploit
    dark_patterns: List[str]  # Any deceptive UX patterns detected


class Persona(TypedDict):
    """A detailed user persona following the India 1, 2, 3 framework."""
    name: str
    segment: str        # "India 1", "India 2", or "India 3"
    age_range: str
    income_bracket: str
    trust_deficit_score: int  # 1-10, how skeptical they are
    language_preference: str  # "English", "Hindi", "Hinglish", etc.
    tech_comfort: str   # "High", "Medium", "Low"
    description: str    # Narrative description of their life and needs


class Feature(TypedDict):
    """A proposed product feature with RICE scoring."""
    name: str
    description: str
    linked_pain: str    # Which verified pain this solves
    linked_lack: str    # Which competitor lack this exploits
    persona_target: str # Which persona benefits most
    # RICE Framework
    reach: int          # How many users affected (estimated)
    impact: int         # 1-3 scale (1=low, 2=medium, 3=high)
    confidence: float   # 0-1, how sure are we about reach/impact
    effort: int         # Person-weeks to build
    rice_score: float   # Calculated: (reach * impact * confidence) / effort


class Financials(TypedDict):
    """Unit economics and financial projections."""
    cac: float              # Customer Acquisition Cost (₹)
    arpu: float             # Average Revenue Per User (₹/month)
    gross_margin: float     # As a decimal (e.g., 0.7 for 70%)
    churn_rate: float       # Monthly churn as a decimal
    ltv: float              # Lifetime Value (calculated)
    ltv_cac_ratio: float    # The magic number (should be > 3)
    payback_months: float   # Months to recover CAC
    pricing_tiers: Dict[str, float]  # e.g., {"Basic": 99, "Pro": 299}


class MarketState(TypedDict):
    """
    The master state object passed through the entire LangGraph pipeline.
    """
    # ===== INPUTS =====
    raw_idea: str
    target_region: str  # Default: "India"
    
    # ===== RESEARCH DATA (Strategist + Critic) =====
    raw_pains: List[Dict[str, Any]]         # Unverified pains from search
    verified_pains: List[VerifiedPain]      # Verified with stats & sentiment
    problem_statement: str                  # "For [Who], [Problem]..."
    delta_4_logic: str                      # Proof of 10x improvement
    
    # ===== COMPETITIVE INTELLIGENCE (Infiltrator + Analyzer) =====
    competitor_table: List[Competitor]
    
    # ===== PERSONAS (Anthropologist) =====
    personas: List[Persona]
    
    # ===== FEATURES (Innovator) =====
    feature_list: List[Feature]
    
    # ===== FINANCIALS (Auditor) =====
    business_model: Dict[str, Any]  # Partners, Value Props, Cost Structure
    revenue_model: Financials
    
    # ===== CONTROL FLAGS =====
    is_verified: bool               # Set by Critic
    is_financially_viable: bool     # Set by Auditor (LTV/CAC > 3)
    iteration_count: int            # Track how many loops we've done
    max_iterations: int             # Prevent infinite loops
    
    # ===== FEEDBACK (for loops) =====
    critic_feedback: Optional[str]      # Why verification failed
    auditor_feedback: Optional[str]     # Why financials failed
    
    # ===== FINAL OUTPUT =====
    final_report_path: Optional[str]    # Path to generated PDF
