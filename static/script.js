/**
 * EduGenie Interactive Frontend Controller
 * Handles task switching, sample chips, asynchronous API calls,
 * Markdown rendering, and the interactive 3-MCQ quiz engine.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const taskTabs = document.querySelectorAll(".tab-btn");
  const taskDropdown = document.getElementById("taskDropdown");
  const sampleChips = document.querySelectorAll(".chip");
  const form = document.getElementById("edugenieForm");
  const inputText = document.getElementById("inputText");
  const contextGroup = document.getElementById("contextGroup");
  const contextText = document.getElementById("contextText");
  const inputLabel = document.getElementById("inputLabel");
  const charCounter = document.getElementById("charCounter");
  const submitBtn = document.getElementById("submitBtn");
  const clearBtn = document.getElementById("clearBtn");
  const spinner = submitBtn.querySelector(".spinner");
  const btnText = submitBtn.querySelector(".btn-text");

  // Result Elements
  const resultSection = document.getElementById("resultSection");
  const resultTypeBadge = document.getElementById("resultTypeBadge");
  const resultTitle = document.getElementById("resultTitle");
  const engineBadge = document.getElementById("engineBadge");
  const generalResultContainer = document.getElementById("generalResultContainer");
  const quizContainer = document.getElementById("quizContainer");
  const quizQuestionsList = document.getElementById("quizQuestionsList");
  const quizScorePill = document.getElementById("quizScorePill");
  const retryQuizBtn = document.getElementById("retryQuizBtn");
  const copyResultBtn = document.getElementById("copyResultBtn");
  const speakResultBtn = document.getElementById("speakResultBtn");

  // State
  let currentTask = "qa";
  let activeQuizData = [];
  let userQuizScores = { answered: 0, correct: 0 };
  let currentRawText = "";
  let isSpeaking = false;

  // Task configuration presets
  const taskConfig = {
    qa: {
      label: "Ask your educational question:",
      placeholder: "e.g. Which is the largest ocean?",
      btnText: "Ask EduGenie",
      endpoint: "/qa",
      badge: "Question Answering",
      showContext: true,
    },
    explain: {
      label: "Concept or topic to explain:",
      placeholder: "e.g. Quantum Computing, Photosynthesis, Theory of Relativity...",
      btnText: "Explain Concept",
      endpoint: "/explain",
      badge: "Concept Explanation",
      showContext: false,
    },
    quiz: {
      label: "Passage or topic for quiz generation:",
      placeholder: "e.g. Paste a paragraph about the Pythagoras Theorem or an academic lesson...",
      btnText: "Generate Quiz (3 MCQs)",
      endpoint: "/quiz",
      badge: "Interactive Assessment",
      showContext: false,
    },
    summarize: {
      label: "Passage to summarize for revision:",
      placeholder: "e.g. Paste a long textbook passage or article here for quick revision...",
      btnText: "Summarize Text",
      endpoint: "/summarize",
      badge: "Revision Summary",
      showContext: false,
    },
    recommend_path: {
      label: "Topic or skill for learning roadmap:",
      placeholder: "e.g. Structured Query Language (SQL), Python for Data Science, Modern Web Dev...",
      btnText: "Generate Learning Path",
      endpoint: "/learn/recommendations",
      badge: "Curriculum Roadmap",
      showContext: false,
    },
  };

  // Sync Task UI
  function setTask(taskKey) {
    if (!taskConfig[taskKey]) return;
    currentTask = taskKey;

    // Update active tab
    taskTabs.forEach((tab) => {
      if (tab.dataset.task === taskKey) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });

    // Update dropdown
    if (taskDropdown.value !== taskKey) {
      taskDropdown.value = taskKey;
    }

    // Update inputs and labels
    const cfg = taskConfig[taskKey];
    inputLabel.textContent = cfg.label;
    inputText.placeholder = cfg.placeholder;
    btnText.textContent = cfg.btnText;

    if (cfg.showContext) {
      contextGroup.style.display = "block";
    } else {
      contextGroup.style.display = "none";
    }
  }

  // Event Listeners for Tabs
  taskTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      setTask(tab.dataset.task);
    });
  });

  // Event Listener for Dropdown
  taskDropdown.addEventListener("change", (e) => {
    setTask(e.target.value);
  });

  // Sample Chips
  sampleChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const task = chip.dataset.task;
      const text = chip.dataset.text;
      setTask(task);
      inputText.value = text;
      updateCharCounter();
      inputText.focus();
      // Auto-trigger submission for quick demonstration
      handleFormSubmit();
    });
  });

  // Character Counter
  function updateCharCounter() {
    const len = inputText.value.length;
    charCounter.textContent = `${len} character${len === 1 ? "" : "s"}`;
  }
  inputText.addEventListener("input", updateCharCounter);

  // Clear Form
  clearBtn.addEventListener("click", () => {
    inputText.value = "";
    if (contextText) contextText.value = "";
    updateCharCounter();
    resultSection.style.display = "none";
    inputText.focus();
  });

  // Form Submit Handler
  async function handleFormSubmit(e) {
    if (e) e.preventDefault();
    const textVal = inputText.value.trim();
    if (!textVal) {
      inputText.focus();
      return;
    }

    const cfg = taskConfig[currentTask];
    let payload = {};

    if (currentTask === "qa") {
      payload = {
        question: textVal,
        context: contextText ? contextText.value.trim() : null,
      };
    } else if (currentTask === "explain") {
      payload = { concept: textVal };
    } else if (currentTask === "quiz") {
      payload = { passage: textVal };
    } else if (currentTask === "summarize") {
      payload = { text: textVal, format_type: "bullet_points" };
    } else if (currentTask === "recommend_path") {
      payload = { topic: textVal, level: "beginner" };
    }

    // Set Loading State
    setLoading(true);

    try {
      const response = await fetch(cfg.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      renderResponse(data, currentTask);
    } catch (err) {
      console.error("EduGenie Request Error:", err);
      renderError(err.message);
    } finally {
      setLoading(false);
    }
  }

  form.addEventListener("submit", handleFormSubmit);

  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    if (isLoading) {
      spinner.style.display = "inline-block";
      btnText.textContent = "Consulting EduGenie...";
    } else {
      spinner.style.display = "none";
      btnText.textContent = taskConfig[currentTask].btnText;
    }
  }

  // Render Response
  function renderResponse(data, task) {
    resultSection.style.display = "block";
    resultTypeBadge.textContent = taskConfig[task].badge;
    engineBadge.textContent = data.model_used || "Google Gemini";

    if (task === "quiz" && Array.isArray(data.quiz) && data.quiz.length > 0) {
      // Interactive Quiz View
      generalResultContainer.style.display = "none";
      quizContainer.style.display = "flex";
      resultTitle.textContent = `Quiz on "${data.topic_or_passage}"`;
      currentRawText = `Quiz on ${data.topic_or_passage}\n\n` + JSON.stringify(data.quiz, null, 2);
      renderQuiz(data.quiz);
    } else {
      // Markdown Formatted Output View
      generalResultContainer.style.display = "block";
      quizContainer.style.display = "none";

      let content = "";
      if (task === "qa") {
        resultTitle.textContent = `Q&A: ${data.question}`;
        content = data.answer;
      } else if (task === "explain") {
        resultTitle.textContent = `Concept: ${data.concept}`;
        content = data.explanation;
      } else if (task === "summarize") {
        resultTitle.textContent = "Summary & Key Takeaways";
        const metaInfo = `> **Compression:** Compressed to ${data.summary_word_count} words (${data.compression_ratio} reduction)\n\n`;
        content = metaInfo + data.summary;
      } else if (task === "recommend_path") {
        resultTitle.textContent = `Roadmap for ${data.topic}`;
        content = data.learning_path;
      }

      currentRawText = content;
      generalResultContainer.innerHTML = window.marked ? window.marked.parse(content) : content;
    }

    // Scroll to results smoothly
    resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderError(errorMessage) {
    resultSection.style.display = "block";
    resultTypeBadge.textContent = "Error";
    resultTitle.textContent = "Request Failed";
    engineBadge.textContent = "System Alert";
    generalResultContainer.style.display = "block";
    quizContainer.style.display = "none";
    generalResultContainer.innerHTML = `
      <div style="background:#fee2e2; border-left:4px solid #ef4444; padding:1rem; border-radius:8px; color:#991b1b;">
        <strong>Error encountered:</strong> ${errorMessage}
        <p style="margin-top:0.5rem; font-size:0.9rem;">
          Tip: Ensure your <code>GEMINI_API_KEY</code> is correctly placed in your <code>.env</code> file.
        </p>
      </div>
    `;
    resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Interactive Quiz Engine
  function renderQuiz(questions) {
    activeQuizData = questions;
    userQuizScores = { answered: 0, correct: 0 };
    updateQuizScoreUI();
    quizQuestionsList.innerHTML = "";

    questions.forEach((q, qIndex) => {
      const card = document.createElement("div");
      card.className = "quiz-question-card";
      card.dataset.questionId = q.id;

      const numBadge = document.createElement("span");
      numBadge.className = "quiz-q-num";
      numBadge.textContent = `Question ${qIndex + 1} of ${questions.length}`;

      const qText = document.createElement("h4");
      qText.className = "quiz-q-text";
      qText.textContent = q.question;

      const optionsGrid = document.createElement("div");
      optionsGrid.className = "quiz-options-grid";

      // Render Options A, B, C, D
      const optionKeys = ["A", "B", "C", "D"];
      optionKeys.forEach((key) => {
        const optionVal = q.options[key] || "";
        if (!optionVal) return;

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "quiz-option-btn";
        btn.dataset.key = key;

        const optBadge = document.createElement("span");
        optBadge.className = "option-badge";
        optBadge.textContent = key;

        const optSpan = document.createElement("span");
        optSpan.className = "option-text";
        optSpan.textContent = optionVal;

        btn.appendChild(optBadge);
        btn.appendChild(optSpan);

        btn.addEventListener("click", () => handleOptionClick(qIndex, key, card, q));
        optionsGrid.appendChild(btn);
      });

      card.appendChild(numBadge);
      card.appendChild(qText);
      card.appendChild(optionsGrid);
      quizQuestionsList.appendChild(card);
    });
  }

  function handleOptionClick(qIndex, chosenKey, cardElement, questionObj) {
    const optionButtons = cardElement.querySelectorAll(".quiz-option-btn");
    const correctKey = questionObj.correct_answer.toUpperCase().trim();
    const isCorrect = chosenKey.toUpperCase().trim() === correctKey;

    // Disable all options for this question
    optionButtons.forEach((btn) => {
      btn.disabled = true;
      const btnKey = btn.dataset.key.toUpperCase().trim();

      if (btnKey === chosenKey) {
        if (isCorrect) {
          btn.classList.add("selected-correct");
        } else {
          btn.classList.add("selected-wrong");
        }
      } else if (btnKey === correctKey && !isCorrect) {
        // Reveal the correct answer in green if the student was wrong
        btn.classList.add("correct-reveal");
      }
    });

    // Add Explanation Box
    const explanationBox = document.createElement("div");
    explanationBox.className = "quiz-explanation-box";
    explanationBox.innerHTML = `
      <strong>${isCorrect ? "✅ Correct!" : "❌ Incorrect."}</strong> 
      ${questionObj.explanation || `The correct answer is Option ${correctKey}.`}
    `;
    cardElement.appendChild(explanationBox);

    // Update Score
    userQuizScores.answered += 1;
    if (isCorrect) userQuizScores.correct += 1;
    updateQuizScoreUI();
  }

  function updateQuizScoreUI() {
    quizScorePill.textContent = `Score: ${userQuizScores.correct} / ${activeQuizData.length}`;
    if (userQuizScores.answered === activeQuizData.length && activeQuizData.length > 0) {
      if (userQuizScores.correct === activeQuizData.length) {
        quizScorePill.style.backgroundColor = "var(--success)";
      } else {
        quizScorePill.style.backgroundColor = "var(--primary)";
      }
    }
  }

  // Retry Quiz Button
  retryQuizBtn.addEventListener("click", () => {
    if (activeQuizData.length > 0) {
      renderQuiz(activeQuizData);
    }
  });

  // Copy to Clipboard
  copyResultBtn.addEventListener("click", async () => {
    if (!currentRawText) return;
    try {
      await navigator.clipboard.writeText(currentRawText);
      const originalText = copyResultBtn.textContent;
      copyResultBtn.textContent = "✓ Copied!";
      setTimeout(() => {
        copyResultBtn.textContent = originalText;
      }, 2000);
    } catch (err) {
      console.error("Clipboard copy failed:", err);
    }
  });

  // Text to Speech
  speakResultBtn.addEventListener("click", () => {
    if (!("speechSynthesis" in window)) {
      alert("Text-to-speech is not supported in this browser.");
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      isSpeaking = false;
      speakResultBtn.textContent = "🔊 Listen";
      return;
    }

    const cleanText = currentRawText.replace(/[#*`_>-]/g, " ").trim();
    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.onend = () => {
      isSpeaking = false;
      speakResultBtn.textContent = "🔊 Listen";
    };
    utterance.onerror = () => {
      isSpeaking = false;
      speakResultBtn.textContent = "🔊 Listen";
    };

    window.speechSynthesis.speak(utterance);
    isSpeaking = true;
    speakResultBtn.textContent = "⏹️ Stop";
  });

  // Initialize Default State
  setTask("qa");
});
