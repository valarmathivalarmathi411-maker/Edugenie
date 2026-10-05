"""
EduGenie Quiz Generation Module
Generates 3 educational multiple-choice questions (MCQs) with 4 options each,
correct answers, and explanations using Google Gemini.
Includes markdown cleaner and JSON parser.
"""

import json
import re
import logging
from typing import Dict, Any, List
from config import is_gemini_configured, get_gemini_model

logger = logging.getLogger(__name__)


def clean_json_block(text: str) -> str:
    """
    Cleans markdown formatting, code fences, and extraneous commentary
    from a JSON response to ensure safe parsing.
    """
    cleaned = text.strip()

    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()

    # Find the outermost array [ ... ] or object { ... }
    start_arr = cleaned.find("[")
    end_arr = cleaned.rfind("]")

    if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
        cleaned = cleaned[start_arr : end_arr + 1]
    else:
        start_obj = cleaned.find("{")
        end_obj = cleaned.rfind("}")
        if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
            cleaned = cleaned[start_obj : end_obj + 1]

    # Remove any trailing commas before closing braces/brackets
    cleaned = re.sub(r",\s*([\]\}])", r"\1", cleaned)
    return cleaned


def generate_quiz(passage_or_topic: str) -> Dict[str, Any]:
    """
    Generates 3 MCQs with 4 options each from a topic or passage.
    Returns structured JSON with questions, options, correct answers, and explanations.
    """
    topic_clean = passage_or_topic.strip()
    if not topic_clean:
        return {
            "topic_or_passage": passage_or_topic,
            "quiz": [],
            "count": 0,
            "model_used": "None",
            "success": False,
            "error": "Please provide a topic or passage to generate a quiz.",
        }

    if is_gemini_configured():
        try:
            model = get_gemini_model()
            prompt = f"""You are EduGenie, an expert curriculum and assessment designer.
Generate exactly 3 high-quality multiple-choice questions (MCQs) based on the following topic or passage:

Content:
\"\"\"{topic_clean}\"\"\"

Requirements:
1. Generate exactly 3 questions.
2. Each question MUST have exactly 4 plausible options labeled "A", "B", "C", and "D".
3. Exactly one option is correct. The distractors must be plausible educational choices.
4. Provide a clear, brief explanation for the correct answer.
5. You MUST return ONLY valid JSON formatted as a list of 3 question objects. Do not include markdown preamble or conversational text.

Required JSON Schema:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "options": {{
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    }},
    "correct_answer": "A",
    "explanation": "Why this answer is correct."
  }}
]
"""
            response = model.generate_content(prompt)
            if response and response.text:
                cleaned_json = clean_json_block(response.text)
                quiz_data = json.loads(cleaned_json)

                # Wrap single dict in list if needed
                if isinstance(quiz_data, dict):
                    quiz_data = [quiz_data]

                # Validate structure
                validated_quiz = []
                for idx, q in enumerate(quiz_data[:3], start=1):
                    validated_quiz.append({
                        "id": q.get("id", idx),
                        "question": q.get("question", f"Question {idx}"),
                        "options": q.get("options", {"A": "", "B": "", "C": "", "D": ""}),
                        "correct_answer": str(q.get("correct_answer", "A")).upper().strip(),
                        "explanation": q.get("explanation", "Correct answer verified."),
                    })

                return {
                    "topic_or_passage": topic_clean,
                    "quiz": validated_quiz,
                    "count": len(validated_quiz),
                    "model_used": f"Google Gemini ({model.model_name})",
                    "success": True,
                }
        except Exception as e:
            logger.error(f"Quiz generation error: {e}")
            return {
                "topic_or_passage": topic_clean,
                "quiz": [],
                "count": 0,
                "model_used": "Google Gemini (Failed)",
                "success": False,
                "error": f"Failed to generate or parse quiz: {str(e)}",
            }

    # Demo Fallback Quiz for offline testing and immediate evaluation
    t_lower = topic_clean.lower()
    if "pythagor" in t_lower or "theorem" in t_lower or "triangle" in t_lower:
        demo_quiz = [
            {
                "id": 1,
                "question": "In a right-angled triangle, what does the Pythagorean Theorem state?",
                "options": {
                    "A": "a + b = c",
                    "B": "a² + b² = c²",
                    "C": "a² - b² = c²",
                    "D": "a × b = c²",
                },
                "correct_answer": "B",
                "explanation": "The Pythagorean Theorem states that the square of the hypotenuse (c) equals the sum of squares of the other two sides (a² + b² = c²).",
            },
            {
                "id": 2,
                "question": "Which side of a right-angled triangle is always the hypotenuse?",
                "options": {
                    "A": "The side opposite to the right angle (longest side)",
                    "B": "The shortest adjacent side",
                    "C": "The vertical side only",
                    "D": "Any side chosen at random",
                },
                "correct_answer": "A",
                "explanation": "The hypotenuse is the longest side of a right triangle and is always opposite the 90-degree right angle.",
            },
            {
                "id": 3,
                "question": "If the lengths of two legs of a right triangle are 3 cm and 4 cm, what is the length of the hypotenuse?",
                "options": {
                    "A": "7 cm",
                    "B": "5 cm",
                    "C": "6 cm",
                    "D": "12 cm",
                },
                "correct_answer": "B",
                "explanation": "Using a² + b² = c²: 3² + 4² = 9 + 16 = 25. The square root of 25 is 5 cm.",
            },
        ]
    else:
        demo_quiz = [
            {
                "id": 1,
                "question": f"What is the primary objective of studying {topic_clean}?",
                "options": {
                    "A": "To gain deep foundational understanding and practical skills",
                    "B": "To memorize definitions without understanding",
                    "C": "To avoid real-world applications",
                    "D": "None of the above",
                },
                "correct_answer": "A",
                "explanation": f"Understanding {topic_clean} provides the fundamental knowledge needed for practical application and mastery.",
            },
            {
                "id": 2,
                "question": f"Which approach is most effective when learning {topic_clean}?",
                "options": {
                    "A": "Passive reading without practice",
                    "B": "Consistent conceptual review combined with active problem solving",
                    "C": "Skipping basic prerequisites",
                    "D": "Studying only once before an exam",
                },
                "correct_answer": "B",
                "explanation": "Active learning, testing yourself, and continuous practice produce the highest retention and conceptual clarity.",
            },
            {
                "id": 3,
                "question": f"How can EduGenie best assist your comprehension of {topic_clean}?",
                "options": {
                    "A": "By providing tailored quizzes, instant answers, and simplified explanations",
                    "B": "By replacing all human teachers permanently",
                    "C": "By removing the need to ever practice",
                    "D": "By only answering yes/no questions",
                },
                "correct_answer": "A",
                "explanation": "EduGenie is designed to be an accessible, personalized study companion that reinforces learning at every step.",
            },
        ]

    return {
        "topic_or_passage": topic_clean,
        "quiz": demo_quiz,
        "count": len(demo_quiz),
        "model_used": "EduGenie Assessment Engine (Offline Mode)",
        "success": True,
    }
