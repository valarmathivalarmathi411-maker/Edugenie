"""
Integration Tests for FastAPI Endpoints
Verifies routing, input validation, status codes, and JSON response contracts.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home_page_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text
    assert "text/html" in response.headers["content-type"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "EduGenie"
    assert "gemini" in data
    assert "supported_features" in data


def test_explain_endpoint_success():
    response = client.post("/explain", json={"concept": "Gravity"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Gravity" in data["concept"]
    assert "explanation" in data


def test_explain_endpoint_missing_input():
    response = client.post("/explain", json={"concept": ""})
    assert response.status_code == 400


def test_qa_endpoint_success():
    response = client.post("/qa", json={"question": "Which is the largest ocean?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Pacific" in data["answer"]


def test_qa_endpoint_empty_question():
    response = client.post("/qa", json={"question": "   "})
    assert response.status_code == 400


def test_quiz_endpoint_success():
    response = client.post("/quiz", json={"passage": "The Pythagoras Theorem"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 3
    assert len(data["quiz"]) == 3
    assert "options" in data["quiz"][0]


def test_quiz_endpoint_missing_content():
    response = client.post("/quiz", json={"passage": ""})
    assert response.status_code == 400


def test_summarize_endpoint_success():
    sample_text = (
        "Artificial Intelligence represents machine-driven cognitive capability. "
        "It includes natural language processing, computer vision, and predictive analytics."
    )
    response = client.post("/summarize", json={"text": sample_text})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data


def test_summarize_endpoint_empty_text():
    response = client.post("/summarize", json={"text": ""})
    assert response.status_code == 400


def test_recommendations_endpoint_success():
    response = client.post("/learn/recommendations", json={"topic": "SQL"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Phase 1" in data["learning_path"]


def test_recommendations_endpoint_empty_topic():
    response = client.post("/learn/recommendations", json={"topic": ""})
    assert response.status_code == 400


def test_unified_api_process():
    # Test unified task router
    response = client.post(
        "/api/process",
        json={"task": "qa", "input_text": "Which is the largest ocean?"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Test invalid task error
    bad_response = client.post(
        "/api/process",
        json={"task": "invalid_task_xyz", "input_text": "Hello"},
    )
    assert bad_response.status_code == 400
