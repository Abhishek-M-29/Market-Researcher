"""
LLM Configuration - Sets up the Gemini model for all agents.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import GOOGLE_API_KEY, GEMINI_MODEL, LLM_TEMPERATURE


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Returns a configured instance of the Gemini LLM.
    
    All agents use the same model to ensure consistent behavior.
    Temperature is set to 0.7 for a balance of creativity and consistency.
    """
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY not found. Please set it in your .env file."
        )
    
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=LLM_TEMPERATURE,
        convert_system_message_to_human=True,  # Gemini compatibility
    )
