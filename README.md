# 📊 Auto EDA Agent

Auto EDA Agent is an **Agentic AI-powered Exploratory Data Analysis (EDA) system** that performs **end-to-end data analysis** on CSV datasets.  
It combines **deterministic Python analytics** with **LLM-driven reasoning and insight generation**, following a true *plan → act → observe → explain* agentic workflow.

This project is designed to demonstrate **production-grade Agentic AI architecture**, not just automated plotting.

---

## 🚀 Key Features

- 📁 Upload any CSV dataset
- 🎯 Define analysis goals in natural language
- 🧠 LLM-powered **EDA planning** (no hardcoded steps)
- 🔧 Deterministic **tool execution layer** (Pandas, Matplotlib, Seaborn)
- 📊 Curated, high-signal visualizations (not chart spam)
- 📉 Intelligent chart prioritization (max 5–8 charts)
- 🔍 Grounded insights with **actual numeric facts**
- 🧩 Clean separation of reasoning, execution, and explanation
- 🖥️ Interactive UI built with Streamlit

---

## 🧠 Agentic AI Architecture

This project follows a **multi-phase Agentic AI design**, inspired by real-world AI systems.

### 🔹 Phase 1 — UI Layer
- Streamlit-based interface
- Dataset upload, goal input, and results display

### 🔹 Phase 2 — Data Intake
- CSV ingestion using Pandas
- Schema detection and preview

### 🔹 Phase 3 — Reasoning (Planning Agent)
- Gemini LLM generates a **step-by-step EDA plan**
- No code execution
- No insights generated at this stage

### 🔹 Phase 4 — Execution (Tool Agent)
- Plan steps mapped to deterministic Python tools
- Controlled execution with **idempotency guards**
- Charts generated only once per analysis
- Visualization limits enforced

### 🔹 Phase 5 — Observation & Insight Agent
- Python computes factual metrics (missing %, distributions, survival rates, etc.)
- LLM generates **grounded insights**
- Strict prompt rules prevent hallucination
- Every insight references numeric facts

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** — UI & interaction
- **Pandas** — Data processing
- **Matplotlib / Seaborn** — Visualizations
- **Google Gemini (LLM)** — Planning & insight generation

    

## 📜 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this project with proper attribution.

---

## 📂 Project Structure

```text
.
├── app.py                 # Main Streamlit application (Agentic AI pipeline)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
└── .streamlit/
    └── secrets.toml       # API keys (ignored by git)