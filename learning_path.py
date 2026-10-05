"""
EduGenie Learning Path Module
Generates personalized, structured, end-to-end learning roadmaps from beginner
to advanced levels with curated resources (books, videos, documentation, projects).
Powered by Google Gemini 1.5 Pro.
"""

import logging
from typing import Dict, Any, Optional
from config import is_gemini_configured, get_gemini_model

logger = logging.getLogger(__name__)


def get_learning_recommendations(topic: str, level: str = "beginner") -> Dict[str, Any]:
    """
    Generates a comprehensive, step-by-step educational roadmap for any topic.
    Includes milestone breakdowns, timelines, key concepts, and curated resources.
    """
    topic_clean = topic.strip()
    if not topic_clean:
        return {
            "topic": topic,
            "learning_path": "Please provide a topic or skill to generate a learning path.",
            "model_used": "None",
            "success": False,
            "error": "Empty topic provided",
        }

    if is_gemini_configured():
        try:
            model = get_gemini_model()
            prompt = f"""You are EduGenie, an expert curriculum architect and academic advisor.
Design a structured, comprehensive, and actionable learning roadmap for:

**Topic / Skill:** {topic_clean}
**Target Starting Level:** {level.title()}

Please format the learning path with markdown using this exact structure:

# 🗺️ Master Learning Roadmap: {topic_clean}

### 🎯 Overview & Learning Goals
Brief summary of what the student will achieve upon completing this roadmap.

---

### 🟢 Phase 1: Beginner Level (Foundational Concepts)
- **Estimated Timeline:** e.g., Weeks 1-2
- **Core Topics:**
  - Topic 1: Key theory and basic syntax/principles
  - Topic 2: Essential tools and environment setup
  - Topic 3: First interactive exercises
- **Recommended Free Resources:**
  - 📖 *Documentation / Articles:* (e.g., MDN, W3Schools, Official Docs)
  - 🎥 *Video Courses / Channels:* (e.g., FreeCodeCamp, Coursera, YouTube)
- **Hands-On Milestone Project:** A simple starter project to build confidence.

---

### 🟡 Phase 2: Intermediate Level (Application & Problem Solving)
- **Estimated Timeline:** e.g., Weeks 3-5
- **Core Topics:**
  - Intermediate patterns, real-world schemas, and data operations
  - Debugging, best practices, and integration
- **Recommended Resources:**
  - 📚 *Books / In-depth Guides:* Standard textbooks or guides
  - 🛠️ *Practice Platforms:* (e.g., LeetCode, Kaggle, Exercism)
- **Hands-On Milestone Project:** An end-to-end project applying core techniques.

---

### 🔴 Phase 3: Advanced Level (Optimization, Architecture & Mastery)
- **Estimated Timeline:** e.g., Weeks 6-8+
- **Core Topics:**
  - Performance tuning, scaling, and advanced concepts
  - Industry standards, security, and edge cases
- **Capstone Project:** A portfolio-worthy capstone project.

---

### 💡 Pro Study Habits for {topic_clean}
3 actionable strategies to maintain consistency, retain information, and overcome hurdles.
"""
            response = model.generate_content(prompt)
            if response and response.text:
                return {
                    "topic": topic_clean,
                    "learning_path": response.text.strip(),
                    "model_used": f"Google Gemini ({model.model_name})",
                    "success": True,
                }
        except Exception as e:
            logger.error(f"Learning path generation error: {e}")
            return {
                "topic": topic_clean,
                "learning_path": (
                    f"Unable to generate learning path via Gemini: {str(e)}. "
                    "Please verify your GEMINI_API_KEY in the .env file."
                ),
                "model_used": "Google Gemini (Failed)",
                "success": False,
                "error": str(e),
            }

    # Demo Fallback Roadmap for offline demonstration (e.g., SQL scenario from doc)
    t_lower = topic_clean.lower()
    if "sql" in t_lower or "database" in t_lower:
        demo_path = (
            "# 🗺️ Master Learning Roadmap: Structured Query Language (SQL)\n\n"
            "### 🎯 Overview & Learning Goals\n"
            "Master relational databases, write efficient queries, build schemas, and analyze data like a pro.\n\n"
            "---\n\n"
            "### 🟢 Phase 1: Beginner Level (Foundational Concepts)\n"
            "- **Estimated Timeline:** 1 - 2 Weeks (5-7 hours/week)\n"
            "- **Core Topics:**\n"
            "  - Relational Database fundamentals (Tables, Rows, Columns, Primary & Foreign Keys)\n"
            "  - Basic Queries: `SELECT`, `FROM`, `WHERE`, `ORDER BY`, `LIMIT`\n"
            "  - Filtering & Logical Operators: `AND`, `OR`, `NOT`, `IN`, `BETWEEN`, `LIKE`\n"
            "- **Recommended Free Resources:**\n"
            "  - 📖 *Documentation:* W3Schools SQL Tutorial & Mode Analytics SQL Tutorial\n"
            "  - 🎥 *Videos:* FreeCodeCamp 4-hour Full Database Course (YouTube)\n"
            "- **Starter Project:** Design a personal book library database and write queries to list books by author.\n\n"
            "---\n\n"
            "### 🟡 Phase 2: Intermediate Level (Joins, Aggregations & Grouping)\n"
            "- **Estimated Timeline:** 3 - 4 Weeks\n"
            "- **Core Topics:**\n"
            "  - Aggregate Functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` with `GROUP BY` and `HAVING`\n"
            "  - Table Relationships & Joins: `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN`\n"
            "  - Subqueries, Unions, and Data Modification: `INSERT`, `UPDATE`, `DELETE`\n"
            "- **Recommended Resources:**\n"
            "  - 📚 *Practice Platforms:* SQLZoo, LeetCode (Database problems), HackerRank\n"
            "- **Milestone Project:** Build an E-Commerce Analytics Query Suite calculating monthly revenue and customer churn.\n\n"
            "---\n\n"
            "### 🔴 Phase 3: Advanced Level (Window Functions, CTEs & Indexing)\n"
            "- **Estimated Timeline:** 5 - 8 Weeks\n"
            "- **Core Topics:**\n"
            "  - Window Functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`)\n"
            "  - Common Table Expressions (CTEs) & Recursive Queries\n"
            "  - Indexing strategies, Query Execution Plans (`EXPLAIN ANALYZE`), and Database Normalization (1NF to 3NF)\n"
            "- **Capstone Project:** Production Database Optimization: Take a million-row dataset and optimize slow queries by 80%.\n\n"
            "---\n\n"
            "### 💡 Pro Study Habits for SQL\n"
            "1. **Never just read SQL:** Always type queries inside SQLite or PostgreSQL.\n"
            "2. **Inspect the table output:** Mentally verify the output row count before hitting run.\n"
            "3. **Practice daily:** Solve one LeetCode or SQLZoo puzzle every morning!\n\n"
            "*(Note: Demo roadmap shown. Add your GEMINI_API_KEY in .env for live AI custom roadmaps.)*"
        )
    else:
        demo_path = (
            f"# 🗺️ Master Learning Roadmap: {topic_clean}\n\n"
            "### 🎯 Overview & Learning Goals\n"
            f"Gain comprehensive mastery in {topic_clean}, progressing systematically from fundamental basics to advanced mastery.\n\n"
            "---\n\n"
            "### 🟢 Phase 1: Beginner Level (Core Foundations)\n"
            "- **Estimated Timeline:** 2 Weeks\n"
            f"- **Core Topics:** Basic definitions, core terminology, environment setup, and fundamental principles of {topic_clean}.\n"
            "- **Recommended Resources:** Free tutorials, official documentation, and community starter guides.\n"
            "- **Milestone Project:** A basic starter project demonstrating key concepts.\n\n"
            "---\n\n"
            "### 🟡 Phase 2: Intermediate Level (Practical Implementation)\n"
            "- **Estimated Timeline:** 3 - 4 Weeks\n"
            "- **Core Topics:** Real-world problem solving, standard workflows, and debugging techniques.\n"
            "- **Milestone Project:** A functional multi-feature application or case study.\n\n"
            "---\n\n"
            "### 🔴 Phase 3: Advanced Level (Optimization & Mastery)\n"
            "- **Estimated Timeline:** 4+ Weeks\n"
            "- **Core Topics:** Advanced architectures, performance optimization, and specialized modern patterns.\n"
            "- **Capstone Project:** A production-ready portfolio project.\n\n"
            "---\n\n"
            "### 💡 Pro Study Habits\n"
            "- Maintain consistent daily practice (even 30 minutes counts).\n"
            "- Build real projects instead of passively watching tutorials.\n\n"
            "*(Note: Demo roadmap shown. Configure your GEMINI_API_KEY in .env for live Gemini roadmaps.)*"
        )

    return {
        "topic": topic_clean,
        "learning_path": demo_path,
        "model_used": "EduGenie Curriculum Engine (Offline Mode)",
        "success": True,
    }
