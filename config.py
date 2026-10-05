"""
EduGenie Configuration Module
Manages environment variables, API configurations, and AI model initializations.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip()

# Local Model configuration (LaMini-Flan-T5)
ENABLE_LOCAL_MODEL: bool = os.getenv("ENABLE_LOCAL_MODEL", "false").lower() in ("true", "1", "yes")
LOCAL_MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "MBZUAI/LaMini-Flan-T5-783M").strip()

# Server Settings
APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1").strip()
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

def is_gemini_configured() -> bool:
    """Check if a valid Gemini API key is configured."""
    return bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")

def get_gemini_model(model_name: Optional[str] = None):
    """
    Initializes and returns a Google Gemini GenerativeModel instance.
    Raises RuntimeError if google-generativeai is not installed or API key is missing.
    """
    if not is_gemini_configured():
        raise ValueError(
            "GEMINI_API_KEY is not set or invalid. Please add your API key to the .env file."
        )

    try:
        import google.generativeai as genai
    except ImportError as e:
        raise ImportError(
            "The 'google-generativeai' package is required. Run 'pip install google-generativeai'."
        ) from e

    genai.configure(api_key=GEMINI_API_KEY)
    target_model = model_name or GEMINI_MODEL
    return genai.GenerativeModel(target_model)
