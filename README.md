# 🎓 EduGenie: Google Gemini Powered Learning Assistant

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini%201.5%20Pro-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

EduGenie is a lightweight, AI-driven educational assistant designed for students, educators, and lifelong learners of all academic levels. It combines cloud-based intelligence (**Google Gemini 1.5 Pro**) and optional local AI inference (**LaMini-Flan-T5-783M**) to deliver an interactive, responsive learning companion with zero clutter.

---

## 🌟 Key Features

1. **💡 Concept Explanation (`/explain`)**:
   - Breaks down complex academic concepts into plain English, real-world analogies, and step-by-step mechanisms.
   - Built to run with **LaMini-Flan-T5-783M** (instruction-tuned, CPU-compatible) or **Google Gemini**.

2. **❓ Question Answering (`/qa`)**:
   - Accurate, structured, and contextual answers to general knowledge and academic questions.
   - Scenario: *"Which is the largest ocean?"* ➔ Instant direct answer, facts, depth metrics, and interesting trivia.

3. **📝 Interactive Quiz Generation (`/quiz`)**:
   - Generates **3 Multiple-Choice Questions (MCQs)** with **4 plausible options** from any topic or passage.
   - **Interactive Frontend UI**: Real-time evaluation! If a student picks the wrong answer, it highlights the selection in red, reveals the correct answer in green, provides an explanation, and tracks live score.

4. **📄 Text Summarization (`/summarize`)**:
   - Condenses lengthy textbook chapters or articles into structured, high-yield study summaries with key bullet points and exam tips.

5. **🗺️ Personalized Learning Roadmap (`/learn/recommendations`)**:
   - Generates full beginner-to-advanced curriculum plans with timelines, milestone projects, and curated learning resources (videos, documentation, books).
   - Scenario: *"SQL"* ➔ Foundation ➔ Joins & Aggregations ➔ CTEs & Window Functions ➔ Capstone optimization project.

---

## 🏗️ Project Architecture

```
EduGenie/
├── main.py                  # FastAPI application entrypoint & API routes
├── explanation_module.py    # Concept explanation (LaMini-Flan-T5 / Gemini)
├── qna.py                   # Question answering engine (Gemini 1.5 Pro)
├── quiz_module.py           # 3-question MCQ generator & JSON cleaner
├── summary_module.py        # Text & passage summarization engine
├── learning_path.py         # Step-by-step curriculum & roadmap generator
├── config.py                # Environment and model configurations
├── requirements.txt         # Project dependencies
├── .env.example             # Example environment configuration
├── .env                     # Local environment file (with API keys)
├── .gitignore               # Git ignore rules
├── templates/
│   └── index.html           # Modern responsive HTML frontend with Jinja2
├── static/
│   ├── style.css            # Custom CSS styling (responsive, light/dark accents)
│   └── script.js            # Frontend logic & interactive quiz engine
├── tests/
│   ├── __init__.py          # Test package init
│   ├── test_modules.py      # Unit tests for all AI modules
│   └── test_api.py          # FastAPI endpoint integration tests
└── .vscode/
    ├── launch.json          # VS Code 1-click debugging configuration
    ├── settings.json        # Python interpreter and pytest workspace settings
    └── extensions.json      # Recommended VS Code extensions
```

---

## 📋 Pre-requisites

- **Python**: Version `3.10+` (Python 3.10, 3.11, or 3.12).
- **Google Gemini API Key**: Free key from [Google AI Studio](https://aistudio.google.com/app/apikey).
- **Git** (optional).

---

## 🚀 Installation & Setup Guide

### Step 1: Clone or Navigate to the Project Directory
```bash
cd /path/to/Edugenie_Rahul
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate on Linux / macOS:
source .venv/bin/activate

# Or on Windows (Command Prompt / PowerShell):
# .venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

> **Note on Local Model (Optional):**
> If you wish to run `MBZUAI/LaMini-Flan-T5-783M` locally on your CPU/GPU, install PyTorch and Transformers:
> ```bash
> pip install torch transformers
> ```
> EduGenie automatically uses Gemini if local models are disabled or if dependencies are not present.

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-1.5-pro
ENABLE_LOCAL_MODEL=False
APP_HOST=127.0.0.1
APP_PORT=8000
```

---

## 💻 Running the Application

### Option A: Via Command Line
With your virtual environment active, run:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Then open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### Option B: Via Visual Studio Code (1-Click Run & Debug)
1. Open this folder in VS Code (`code .`).
2. Press `Ctrl + Shift + D` (or `Cmd + Shift + D` on macOS) to open the **Run & Debug** panel.
3. Select **"EduGenie: FastAPI Server"** from the dropdown at the top.
4. Press `F5` (or click the green Play icon).
5. VS Code will automatically start the Uvicorn server in the integrated terminal with hot-reloading and active debugger support!

---

## 🧪 Running the Automated Test Suite

EduGenie includes automated unit and integration tests using `pytest`.

Run all tests:
```bash
pytest -v tests/
```

Or run individual test modules:
```bash
# Test AI logic modules
pytest -v tests/test_modules.py

# Test FastAPI HTTP endpoints
pytest -v tests/test_api.py
```

---

## 📚 REST API Reference

Interactive OpenAPI documentation is automatically available when the server is running:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

| Method | Endpoint | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | — | Renders the EduGenie Web Interface |
| `POST` | `/qa` | `{"question": "...", "context": "..."}` | Solves academic and general questions |
| `POST` | `/explain` | `{"concept": "..."}` | Explains concepts with simplified analogies |
| `POST` | `/quiz` | `{"passage": "..."}` | Generates 3 MCQs with 4 options each |
| `POST` | `/summarize` | `{"text": "...", "format_type": "..."}` | Summarizes long educational passages |
| `POST` | `/learn/recommendations` | `{"topic": "...", "level": "..."}` | Generates milestone learning roadmap |
| `POST` | `/api/process` | `{"task": "...", "input_text": "..."}` | Unified process endpoint |
| `GET` | `/health` | — | System health check and model diagnostics |

---

## 🎯 Example Walkthroughs

### 1. Asking Questions
- **Query:** `Which is the largest ocean?`
- **Output:** Identifies the Pacific Ocean, highlights its surface area (>165 million sq km), Mariana Trench depth, bordering continents, and interesting trivia.

### 2. Generating Quizzes
- **Passage:** `The Pythagoras Theorem states that in a right-angled triangle...`
- **Output:** 3 multiple choice questions with clickable options (A, B, C, D). Real-time correctness validation with explanations and live score calculation!

### 3. Step-by-Step Learning Roadmaps
- **Topic:** `Structured Query Language (SQL)`
- **Output:** Organized into Phase 1 (Foundations), Phase 2 (Joins & Aggregations), Phase 3 (Window Functions & Indexing) with curated links to free tutorials, practice platforms, and projects.

---

## 🛠️ Technology Stack
- **Backend**: FastAPI, Uvicorn, Pydantic, Python-dotenv
- **AI & LLM**: Google Gemini 1.5 Pro (`google-generativeai`), LaMini-Flan-T5-783M (`transformers`, `torch`)
- **Frontend**: HTML5, Modern CSS3 with CSS Variables, Vanilla JS (ES6+), Marked.js (Markdown)
- **Testing**: Pytest, Starlette TestClient, Unittest Mock
- **IDE Integration**: Visual Studio Code Launch Configurations, Settings, and Extension Recommendations
