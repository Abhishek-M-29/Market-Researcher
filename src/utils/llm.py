"""
LLM Configuration - Dual LLM system for optimal performance.

- Perplexity (sonar-pro): Research & fact-finding (has built-in web search)
- Gemini: Analysis & synthesis (better at structured output)
"""

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import (
    PERPLEXITY_API_KEY, PERPLEXITY_MODEL,
    GOOGLE_API_KEY, GEMINI_MODEL,
    LLM_TEMPERATURE
)


def get_research_llm() -> ChatOpenAI:
    """
    Returns Perplexity LLM for research tasks.
    
    Best for: Strategist, Critic, Infiltrator
    - Built-in web search capabilities
    - Good at finding facts and citations
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError(
            "PERPLEXITY_API_KEY not found. Please set it in your .env file."
        )
    
    return ChatOpenAI(
        model=PERPLEXITY_MODEL,
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai",
        temperature=LLM_TEMPERATURE,
    )


def get_analysis_llm() -> ChatGoogleGenerativeAI:
    """
    Returns Gemini LLM for analysis tasks.
    
    Best for: Anthropologist, Analyzer, Innovator, Auditor, PDF Compiler
    - Better at structured output and synthesis
    - Good at creative and analytical tasks
    """
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY not found. Please set it in your .env file."
        )
    
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=LLM_TEMPERATURE,
        convert_system_message_to_human=True,
    )


def get_llm():
    """
    Default LLM - returns Perplexity for backward compatibility.
    Prefer using get_research_llm() or get_analysis_llm() directly.
    """
    return get_research_llm()
