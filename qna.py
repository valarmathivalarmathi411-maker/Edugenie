"""
EduGenie Question Answering (QnA) Module
Powered by Google Gemini 1.5 Pro for accurate, student-friendly answers
to academic, scientific, and general knowledge questions.
"""

import logging
from typing import Dict, Any, Optional
from config import is_gemini_configured, get_gemini_model

logger = logging.getLogger(__name__)


def answer_question(question: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Answers an educational or academic question using Google Gemini.
    Optionally incorporates supporting passage context.
    """
    question_clean = question.strip()
    if not question_clean:
        return {
            "question": question,
            "answer": "Please ask a valid question.",
            "model_used": "None",
            "success": False,
            "error": "Empty question provided",
        }

    if is_gemini_configured():
        try:
            model = get_gemini_model()
            prompt = f"""You are EduGenie, an intelligent, patient, and encouraging AI tutor.
A student has asked the following question:

Question: {question_clean}
"""
            if context and context.strip():
                prompt += f"\nContext/Reference Material:\n{context.strip()}\n"

            prompt += """
Please answer the question accurately, following these educational guidelines:
1. Provide a direct, concise answer first.
2. Provide a brief explanation or breakdown with bullet points for clarity.
3. If relevant, include an interesting "Did you know?" fact to spark curiosity.
4. Keep the language clear, supportive, and accessible to learners.
"""

            response = model.generate_content(prompt)
            if response and response.text:
                return {
                    "question": question_clean,
                    "answer": response.text.strip(),
                    "model_used": f"Google Gemini ({model.model_name})",
                    "success": True,
                }
        except Exception as e:
            logger.error(f"Gemini QnA error: {e}")
            return {
                "question": question_clean,
                "answer": (
                    f"Unable to process question via Gemini: {str(e)}. "
                    "Please verify your GEMINI_API_KEY in the .env file."
                ),
                "model_used": "Google Gemini (Failed)",
                "success": False,
                "error": str(e),
            }

    # Offline/Demo Mode Answer if API Key is not set
    q_lower = question_clean.lower()
    if "ocean" in q_lower and ("largest" in q_lower or "biggest" in q_lower):
        demo_answer = (
            "**Direct Answer:** The **Pacific Ocean** is the largest and deepest ocean on Earth.\n\n"
            "**Key Facts:**\n"
            "- **Surface Area:** Over 165 million square kilometers (63 million square miles), "
            "covering more than 30% of the Earth's surface.\n"
            "- **Deepest Point:** The Challenger Deep in the Mariana Trench reaches approximately 10,994 meters (36,070 feet).\n"
            "- **Bordering Continents:** Asia and Australia to the west, and the Americas to the east.\n\n"
            "🌟 **Did you know?** The Pacific Ocean is so vast that all of the Earth's continents could fit inside its basin with room to spare!\n\n"
            "*(Note: Demo response shown. Add your GEMINI_API_KEY to .env for full live AI Q&A.)*"
        )
    else:
        demo_answer = (
            f"**Answer to:** *{question_clean}*\n\n"
            "EduGenie AI tutors are ready to answer your questions accurately and comprehensively. "
            "To connect with live Gemini 1.5 Pro inference, ensure your `GEMINI_API_KEY` is specified in `.env`.\n\n"
            "**Study Tip:** Breaking down complex queries into specific questions (Who, What, Why, How) "
            "helps deepen conceptual mastery!"
        )

    return {
        "question": question_clean,
        "answer": demo_answer,
        "model_used": "EduGenie Educational QnA Engine",
        "success": True,
    }
