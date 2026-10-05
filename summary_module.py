"""
EduGenie Summarization Module
Utilizes Google Gemini to distill lengthy academic passages and articles into
concise, high-impact summaries perfect for rapid revision and study.
"""

import logging
from typing import Dict, Any, Optional
from config import is_gemini_configured, get_gemini_model

logger = logging.getLogger(__name__)


def summarize_text(text: str, format_type: str = "bullet_points") -> Dict[str, Any]:
    """
    Summarizes long educational text into concise, high-retention study notes.
    """
    text_clean = text.strip()
    if not text_clean:
        return {
            "original_length": 0,
            "summary": "Please provide educational text to summarize.",
            "model_used": "None",
            "success": False,
            "error": "Empty text provided",
        }

    original_word_count = len(text_clean.split())

    if is_gemini_configured():
        try:
            model = get_gemini_model()
            prompt = f"""You are EduGenie, an expert educational revision assistant.
Summarize the following educational text for quick revision.

Source Material:
\"\"\"{text_clean}\"\"\"

Please follow this structured format:
### 📌 Quick Executive Summary
A concise 2-3 sentence overview capturing the core message.

### 🔑 Key Takeaways & Core Concepts
- Bullet point 1: Core insight with bolded key terms.
- Bullet point 2: Key mechanism, relationship, or principle.
- Bullet point 3: Consequence, impact, or application.
(Include up to 5 clear bullet points)

### 💡 High-Yield Study Tip
One actionable tip or mnemonic to help retain this information for exams.

Ensure complete factual accuracy, zero redundancy, and an easy-to-read style.
"""
            response = model.generate_content(prompt)
            if response and response.text:
                summary_text = response.text.strip()
                summary_word_count = len(summary_text.split())
                return {
                    "original_word_count": original_word_count,
                    "summary_word_count": summary_word_count,
                    "compression_ratio": f"{round((1 - summary_word_count / max(original_word_count, 1)) * 100, 1)}%",
                    "summary": summary_text,
                    "model_used": f"Google Gemini ({model.model_name})",
                    "success": True,
                }
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return {
                "original_word_count": original_word_count,
                "summary": (
                    f"Unable to generate summary via Gemini: {str(e)}. "
                    "Please check your GEMINI_API_KEY in the .env file."
                ),
                "model_used": "Google Gemini (Failed)",
                "success": False,
                "error": str(e),
            }

    # Demo Fallback Summary if API key is not configured
    demo_summary = (
        "### 📌 Quick Executive Summary\n"
        "The provided passage highlights essential foundational ideas, explaining the core relationships "
        "and primary components necessary for academic understanding.\n\n"
        "### 🔑 Key Takeaways & Core Concepts\n"
        "- **Core Thesis:** The subject revolves around systemic interactions producing predictable outcomes.\n"
        "- **Key Elements:** Core variables act in unison to govern the overall process.\n"
        "- **Relevance:** Understanding these basic mechanisms enables learners to solve complex related problems.\n\n"
        "### 💡 High-Yield Study Tip\n"
        "Review the key terms in bold and try explaining them aloud without looking at your notes!\n\n"
        "*(Note: Demo summary shown. Configure your GEMINI_API_KEY in .env for live Gemini summarization.)*"
    )
    summary_words = len(demo_summary.split())

    return {
        "original_word_count": original_word_count,
        "summary_word_count": summary_words,
        "compression_ratio": f"{round((1 - summary_words / max(original_word_count, 1)) * 100, 1)}%",
        "summary": demo_summary,
        "model_used": "EduGenie Revision Engine (Offline Mode)",
        "success": True,
    }
