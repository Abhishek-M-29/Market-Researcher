"""
Centralized configuration for the Market Research Engine.
All API keys, model settings, and scoring weights live here.
"""

import os
from dotenv import load_dotenv

# Force reload .env to pick up any changes
load_dotenv(override=True)

# ===== API KEYS =====
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

# ===== MODEL SETTINGS =====
# Perplexity for research/fact-finding (Strategist, Critic, Infiltrator)
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
# Gemini for analysis/synthesis (Anthropologist, Analyzer, Innovator, Auditor, PDF Compiler)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# ===== DOMAIN TRUST SCORES =====
# Used by the Critic to weight the reliability of sources.
# Higher score = more trustworthy.
DOMAIN_TRUST_SCORES = {
    # Government & Academic
    ".gov.in": 10,
    ".gov": 9,
    ".edu": 9,
    ".ac.in": 9,
    
    # Top-Tier Business News (India)
    "economictimes.com": 8,
    "livemint.com": 8,
    "moneycontrol.com": 8,
    "business-standard.com": 8,
    
    # Startup/Tech News (India)
    "inc42.com": 7,
    "yourstory.com": 7,
    "entrackr.com": 7,
    "techcrunch.com": 7,
    
    # International Business
    "reuters.com": 8,
    "bloomberg.com": 8,
    "forbes.com": 7,
    
    # Social/Community (valuable for sentiment, less for stats)
    "reddit.com": 4,
    "twitter.com": 3,
    "quora.com": 3,
    
    # Default for unknown domains
    "default": 2,
}

# Minimum confidence score required for a pain point to be "verified"
MIN_CONFIDENCE_THRESHOLD = 15

# ===== SENTIMENT THRESHOLDS =====
# Only problems with sentiment below this are considered "real pain"
# VADER scores range from -1 (negative) to +1 (positive)
MAX_SENTIMENT_FOR_PAIN = -0.3  # Anything above this is "not painful enough"

# ===== FINANCIAL VIABILITY =====
# The Auditor will reject ideas where LTV/CAC is below this
MIN_LTV_CAC_RATIO = 3.0

# ===== LOOP LIMITS =====
MAX_VERIFICATION_LOOPS = 3
MAX_VIABILITY_LOOPS = 2

# ===== DARK PATTERN KEYWORDS =====
# The Infiltrator will flag competitor sites containing these phrases
DARK_PATTERN_KEYWORDS = [
    "call to cancel",
    "contact support to cancel",
    "cancellation fee",
    "no refund",
    "auto-renew",
    "limited time",
    "act now",
    "only X left",
    "others are viewing",
    "price increase",
]

# ===== PERSONA SEGMENTS =====
INDIA_SEGMENTS = {
    "India 1": {
        "description": "English-first, high-income, tech-savvy urban professionals",
        "population_range": "50M-100M",
        "income": "> ₹15 LPA",
    },
    "India 2": {
        "description": "UPI-native, Hinglish-preferred, value-driven middle class",
        "population_range": "100M-300M",
        "income": "₹3-15 LPA",
    },
    "India 3": {
        "description": "Offline-to-online, trust-based commerce, vernacular-first",
        "population_range": "500M+",
        "income": "< ₹3 LPA",
    },
}
