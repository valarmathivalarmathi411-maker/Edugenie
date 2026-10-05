"""
EduGenie Concept Explanation Module
Utilizes LaMini-Flan-T5 (or Gemini fallback) to deliver simplified,
beginner-friendly explanations for complex academic and scientific concepts.
"""

import logging
from typing import Dict, Any, Optional
from config import (
    ENABLE_LOCAL_MODEL,
    LOCAL_MODEL_NAME,
    is_gemini_configured,
    get_gemini_model,
)

logger = logging.getLogger(__name__)

# Cached local pipeline instance
_local_pipeline = None
_local_load_attempted = False


def _get_local_pipeline():
    """Lazily load the LaMini-Flan-T5 pipeline if enabled and dependencies are present."""
    global _local_pipeline, _local_load_attempted
    if _local_load_attempted:
        return _local_pipeline

    _local_load_attempted = True
    if not ENABLE_LOCAL_MODEL:
        logger.info("Local model disabled via configuration. Using Gemini fallback.")
        return None

    try:
        from transformers import pipeline
        logger.info(f"Loading local model '{LOCAL_MODEL_NAME}' via transformers...")
        _local_pipeline = pipeline(
            "text2text-generation",
            model=LOCAL_MODEL_NAME,
            max_length=512,
            truncation=True
        )
        logger.info("Local model loaded successfully.")
        return _local_pipeline
    except Exception as e:
        logger.warning(
            f"Could not load local model '{LOCAL_MODEL_NAME}': {e}. Falling back to Gemini."
        )
        _local_pipeline = None
        return None


def explain_concept(concept: str) -> Dict[str, Any]:
    """
    Explains an educational concept in simple, accessible language.
    Prioritizes local LaMini-Flan-T5 model if enabled, otherwise uses Gemini.
    """
    concept_clean = concept.strip()
    if not concept_clean:
        return {
            "concept": concept,
            "explanation": "Please provide a concept or topic to explain.",
            "model_used": "None",
            "success": False,
            "error": "Empty concept query",
        }

    # 1. Attempt Local LaMini-Flan-T5 Model
    local_pipe = _get_local_pipeline()
    if local_pipe:
        try:
            prompt = (
                f"Explain the concept of '{concept_clean}' in simple, easy-to-understand "
                f"terms for a student. Include key definitions, practical examples, and an analogy."
            )
            outputs = local_pipe(prompt, max_length=512, do_sample=False)
            generated_text = outputs[0]["generated_text"].strip()
            return {
                "concept": concept_clean,
                "explanation": generated_text,
                "model_used": f"LaMini-Flan-T5 ({LOCAL_MODEL_NAME})",
                "success": True,
            }
        except Exception as e:
            logger.error(f"Local inference error: {e}. Falling back to Gemini.")

    # 2. Attempt Google Gemini Model
    if is_gemini_configured():
        try:
            model = get_gemini_model()
            prompt = f"""You are EduGenie, an expert educational mentor.
Explain the concept '{concept_clean}' in a clear, engaging, and simplified manner for students of any level.

Structure your response using:
1. **Core Concept in Plain English**: A simple 1-2 sentence definition without jargon.
2. **Real-World Analogy**: An intuitive metaphor comparing it to everyday life.
3. **How It Works**: 3-4 clear step-by-step points.
4. **Key Takeaway**: One memorable sentence to remember.

Keep the tone encouraging, lucid, and educational."""

            response = model.generate_content(prompt)
            if response and response.text:
                return {
                    "concept": concept_clean,
                    "explanation": response.text.strip(),
                    "model_used": f"Google Gemini ({model.model_name})",
                    "success": True,
                }
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return {
                "concept": concept_clean,
                "explanation": (
                    f"Unable to generate explanation via Gemini: {str(e)}. "
                    "Please check your GEMINI_API_KEY in the .env file."
                ),
                "model_used": "Google Gemini (Failed)",
                "success": False,
                "error": str(e),
            }

    # 3. Fallback Educational Template if API Key is not yet configured
    demo_explanation = (
        f"### 💡 Understanding: {concept_clean}\n\n"
        f"**1. Core Concept in Plain English:**\n"
        f"{concept_clean} is a foundational concept. At its core, it describes a system or principle "
        f"governing how elements interact and produce observable results.\n\n"
        f"**2. Real-World Analogy:**\n"
        f"Imagine {concept_clean} like a recipe in a kitchen: specific ingredients (inputs) follow precise steps "
        f"(rules or laws) to create a delicious dish (the outcome).\n\n"
        f"**3. Key Pillars:**\n"
        f"- **Foundation:** Starts with basic elements and observed facts.\n"
        f"- **Mechanism:** Operates according to verified patterns or formulas.\n"
        f"- **Application:** Applied in science, technology, and real-world problem-solving.\n\n"
        f"**4. Key Takeaway:**\n"
        f"Mastering {concept_clean} gives you a powerful mental model to understand more complex topics!\n\n"
        f"*(Note: Demo response shown. Add your GEMINI_API_KEY to .env for full live AI explanations.)*"
    )

    return {
        "concept": concept_clean,
        "explanation": demo_explanation,
        "model_used": "EduGenie Offline Educational Engine",
        "success": True,
    }
