"""
EduGenie: Google Gemini Powered Learning Assistant
Main FastAPI Application Entrypoint
"""

import os
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
from explanation_module import explain_concept
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("edugenie")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown routines."""
    logger.info("Initializing EduGenie Learning Assistant...")
    logger.info(f"Gemini Configured: {config.is_gemini_configured()}")
    logger.info(f"Local Model Enabled: {config.ENABLE_LOCAL_MODEL}")
    yield
    logger.info("Shutting down EduGenie Assistant.")


# Initialize FastAPI App
app = FastAPI(
    title="EduGenie - AI Learning Assistant",
    description="Intelligent AI-powered study companion with Gemini and LaMini-Flan-T5",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static and templates directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Mount Static Files & Jinja2 Templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ==========================================
# Pydantic Schemas for API Requests
# ==========================================
class ExplainRequest(BaseModel):
    concept: Optional[str] = None
    text: Optional[str] = None

    def get_query(self) -> str:
        return (self.concept or self.text or "").strip()


class QnARequest(BaseModel):
    question: str
    context: Optional[str] = None


class QuizRequest(BaseModel):
    passage: Optional[str] = None
    topic: Optional[str] = None

    def get_content(self) -> str:
        return (self.passage or self.topic or "").strip()


class SummarizeRequest(BaseModel):
    text: str
    format_type: Optional[str] = "bullet_points"


class LearningPathRequest(BaseModel):
    topic: str
    level: Optional[str] = "beginner"


class UnifiedTaskRequest(BaseModel):
    task: str = Field(..., description="Task type: explain, qa, quiz, summarize, or recommend_path")
    input_text: str = Field(..., description="User query, passage, or topic")
    context: Optional[str] = None
    level: Optional[str] = "beginner"


# ==========================================
# Frontend Routes
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """Renders the main EduGenie web interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "gemini_ready": config.is_gemini_configured(),
            "gemini_model": config.GEMINI_MODEL,
            "local_model_enabled": config.ENABLE_LOCAL_MODEL,
        },
    )


# ==========================================
# REST API Endpoints
# ==========================================
@app.post("/explain")
async def handle_explain(payload: ExplainRequest):
    """Concept Explanation Endpoint."""
    query = payload.get_query()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Concept or text parameter is required.",
        )
    result = explain_concept(query)
    return JSONResponse(content=result)


@app.post("/qa")
async def handle_qa(payload: QnARequest):
    """Question Answering Endpoint."""
    if not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )
    result = answer_question(payload.question, payload.context)
    return JSONResponse(content=result)


@app.post("/quiz")
async def handle_quiz(payload: QuizRequest):
    """Quiz Generation Endpoint (3 MCQs with 4 options each)."""
    content = payload.get_content()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passage or topic parameter is required.",
        )
    result = generate_quiz(content)
    return JSONResponse(content=result)


@app.post("/summarize")
async def handle_summarize(payload: SummarizeRequest):
    """Summarization Endpoint."""
    if not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty.",
        )
    result = summarize_text(payload.text, payload.format_type or "bullet_points")
    return JSONResponse(content=result)


@app.post("/learn/recommendations")
async def handle_recommendations(payload: LearningPathRequest):
    """Learning Path Recommendations Endpoint."""
    if not payload.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty.",
        )
    result = get_learning_recommendations(payload.topic, payload.level or "beginner")
    return JSONResponse(content=result)


@app.post("/api/process")
async def handle_unified_process(payload: UnifiedTaskRequest):
    """Unified endpoint supporting all 5 EduGenie activities from web form."""
    task = payload.task.lower().strip()
    text = payload.input_text.strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text is required.",
        )

    if task in ("explain", "explanation"):
        return JSONResponse(content=explain_concept(text))
    elif task in ("qa", "qna", "question"):
        return JSONResponse(content=answer_question(text, payload.context))
    elif task in ("quiz", "generate_quiz"):
        return JSONResponse(content=generate_quiz(text))
    elif task in ("summarize", "summary"):
        return JSONResponse(content=summarize_text(text))
    elif task in ("recommend_path", "learning_path", "learn"):
        return JSONResponse(content=get_learning_recommendations(text, payload.level or "beginner"))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown task type: '{payload.task}'. Choose from explain, qa, quiz, summarize, recommend_path.",
        )


@app.get("/api/status")
@app.get("/health")
async def get_system_status():
    """System health check and engine capability diagnostics."""
    return {
        "status": "healthy",
        "app_name": "EduGenie",
        "version": "1.0.0",
        "gemini": {
            "configured": config.is_gemini_configured(),
            "model": config.GEMINI_MODEL,
        },
        "local_model": {
            "enabled": config.ENABLE_LOCAL_MODEL,
            "name": config.LOCAL_MODEL_NAME,
        },
        "supported_features": [
            "Concept Explanation (/explain)",
            "Question Answering (/qa)",
            "Quiz Generation (/quiz)",
            "Text Summarization (/summarize)",
            "Learning Recommendations (/learn/recommendations)",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True,
    )
