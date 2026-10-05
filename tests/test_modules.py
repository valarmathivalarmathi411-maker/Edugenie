"""
Unit Tests for EduGenie AI Core Modules
Tests logic for explanation, QnA, quiz generation, summarization, and learning paths.
"""

import pytest
from unittest.mock import patch, MagicMock

from explanation_module import explain_concept
from qna import answer_question
from quiz_module import generate_quiz, clean_json_block
from summary_module import summarize_text
from learning_path import get_learning_recommendations


class TestJsonCleaner:
    def test_clean_plain_json(self):
        raw = '[{"question": "Q1", "correct_answer": "A"}]'
        cleaned = clean_json_block(raw)
        assert cleaned == raw

    def test_clean_fenced_json(self):
        raw = "```json\n[{\"question\": \"Q1\", \"correct_answer\": \"A\"}]\n```"
        cleaned = clean_json_block(raw)
        assert cleaned == '[{"question": "Q1", "correct_answer": "A"}]'

    def test_clean_trailing_comma(self):
        raw = '```json\n[{"id": 1, "answer": "B",}]\n```'
        cleaned = clean_json_block(raw)
        assert cleaned == '[{"id": 1, "answer": "B"}]'

    def test_clean_with_preamble(self):
        raw = 'Here is the requested quiz:\n```json\n[{"id": 1}]\n```\nHope this helps!'
        cleaned = clean_json_block(raw)
        assert cleaned == '[{"id": 1}]'


class TestExplanationModule:
    def test_empty_concept(self):
        res = explain_concept("")
        assert res["success"] is False
        assert "error" in res

    def test_valid_concept_offline_or_online(self):
        res = explain_concept("Photosynthesis")
        assert res["success"] is True
        assert "Photosynthesis" in res["concept"]
        assert len(res["explanation"]) > 20
        assert "model_used" in res

    @patch("explanation_module.is_gemini_configured", return_value=True)
    @patch("explanation_module.get_gemini_model")
    def test_gemini_mocked_explanation(self, mock_get_model, mock_is_configured):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Photosynthesis is the process used by plants."
        mock_model.generate_content.return_value = mock_response
        mock_model.model_name = "gemini-1.5-pro"
        mock_get_model.return_value = mock_model

        res = explain_concept("Photosynthesis")
        assert res["success"] is True
        assert "plants" in res["explanation"]
        assert "Google Gemini" in res["model_used"]


class TestQnAModule:
    def test_empty_question(self):
        res = answer_question("")
        assert res["success"] is False
        assert "error" in res

    def test_largest_ocean_query(self):
        res = answer_question("Which is the largest ocean?")
        assert res["success"] is True
        assert "Pacific Ocean" in res["answer"]

    @patch("qna.is_gemini_configured", return_value=True)
    @patch("qna.get_gemini_model")
    def test_gemini_mocked_qna(self, mock_get_model, mock_is_configured):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "The Pacific Ocean is the largest ocean."
        mock_model.generate_content.return_value = mock_response
        mock_model.model_name = "gemini-1.5-pro"
        mock_get_model.return_value = mock_model

        res = answer_question("Which is the largest ocean?")
        assert res["success"] is True
        assert "Pacific" in res["answer"]


class TestQuizModule:
    def test_empty_passage(self):
        res = generate_quiz("")
        assert res["success"] is False
        assert res["count"] == 0

    def test_pythagoras_quiz_structure(self):
        res = generate_quiz("The Pythagoras Theorem")
        assert res["success"] is True
        assert res["count"] == 3
        assert len(res["quiz"]) == 3

        first_q = res["quiz"][0]
        assert "question" in first_q
        assert "options" in first_q
        assert "correct_answer" in first_q
        assert len(first_q["options"]) == 4
        assert first_q["correct_answer"] in ["A", "B", "C", "D"]

    @patch("quiz_module.is_gemini_configured", return_value=True)
    @patch("quiz_module.get_gemini_model")
    def test_gemini_mocked_quiz(self, mock_get_model, mock_is_configured):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """```json
[
  {
    "id": 1,
    "question": "What is the capital of France?",
    "options": {"A": "Paris", "B": "London", "C": "Rome", "D": "Berlin"},
    "correct_answer": "A",
    "explanation": "Paris is the capital of France."
  },
  {
    "id": 2,
    "question": "What is 2 + 2?",
    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
    "correct_answer": "B",
    "explanation": "2 plus 2 equals 4."
  },
  {
    "id": 3,
    "question": "What is the color of chlorophyll?",
    "options": {"A": "Red", "B": "Blue", "C": "Green", "D": "Yellow"},
    "correct_answer": "C",
    "explanation": "Chlorophyll reflects green light."
  }
]
```"""
        mock_model.generate_content.return_value = mock_response
        mock_model.model_name = "gemini-1.5-pro"
        mock_get_model.return_value = mock_model

        res = generate_quiz("General Knowledge")
        assert res["success"] is True
        assert res["count"] == 3
        assert res["quiz"][0]["correct_answer"] == "A"
        assert res["quiz"][0]["options"]["A"] == "Paris"


class TestSummaryModule:
    def test_empty_text(self):
        res = summarize_text("")
        assert res["success"] is False
        assert "error" in res

    def test_valid_text_summary(self):
        sample = (
            "Machine learning is a branch of artificial intelligence and computer science "
            "which focuses on the use of data and algorithms to imitate the way that humans learn, "
            "gradually improving its accuracy."
        )
        res = summarize_text(sample)
        assert res["success"] is True
        assert "summary" in res
        assert res["original_word_count"] > 0

    @patch("summary_module.is_gemini_configured", return_value=True)
    @patch("summary_module.get_gemini_model")
    def test_gemini_mocked_summary(self, mock_get_model, mock_is_configured):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Summary: Machine learning imitates human learning."
        mock_model.generate_content.return_value = mock_response
        mock_model.model_name = "gemini-1.5-pro"
        mock_get_model.return_value = mock_model

        res = summarize_text("Long text content here...")
        assert res["success"] is True
        assert "Machine learning" in res["summary"]


class TestLearningPathModule:
    def test_empty_topic(self):
        res = get_learning_recommendations("")
        assert res["success"] is False
        assert "error" in res

    def test_sql_learning_path(self):
        res = get_learning_recommendations("SQL")
        assert res["success"] is True
        assert "SQL" in res["topic"]
        assert "Phase 1" in res["learning_path"]
        assert "Phase 2" in res["learning_path"]
        assert "Phase 3" in res["learning_path"]
