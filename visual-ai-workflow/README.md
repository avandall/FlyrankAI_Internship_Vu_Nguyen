# Visual AI Workflow Builder & Inngest Execution Engine

A visual AI workflow system where each node represents an AI decision step that evaluates input context and returns strictly **YES** or **NO**.
The workflow execution is orchestrated step-by-step through **Inngest (Python)** and evaluated via **Groq LLM SDK** (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`), visualized dynamically using **React Flow**.

---

## ✨ Features (Phases 1 - 4)

- 🎨 **Visual Graph Canvas (React Flow)**: Interactive drag-and-drop workflow canvas with pan, zoom, minimap, and custom draggable decision nodes.
- 🔀 **Binary Decision Nodes**: Each node contains an editable prompt and two explicit output ports: **YES (Green)** and **NO (Red)**.
- ⚡ **Inngest Workflow Engine**: Step-by-step graph traversal where each node execution runs in an isolated `step.run()` with automatic retries and durability.
- 🚀 **Groq LLM Integration**: Ultra-fast JSON decision evaluation (`{"decision": "YES" | "NO", "reasoning": "..."}`) with offline fallback.
- 🌟 **Live Visual Execution**: Active nodes pulse during evaluation, visited edges animate with glowing strokes, and completed nodes highlight their outcome.
- 📜 **Execution Inspector**: Live right-hand log panel detailing every decision step, reasoning, and latency in milliseconds.
- 💾 **Export / Import & Presets**: Export workflows to `.json`, import existing graphs, or select from built-in templates (Customer Support Triage, Content Moderation).

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Groq API Key (from [console.groq.com](https://console.groq.com))

### 2. Run Backend (FastAPI + Inngest)
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # (Optional: Add your GROQ_API_KEY)
python -m uvicorn app.main:app --port 8000 --reload
```
API runs at: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`)

### 3. Run Frontend (React Flow + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open your browser at: `http://localhost:5173`

### 4. Run Inngest Dev Server (Optional)
```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```
Inngest Dashboard at: `http://localhost:8288`

---

## 🧪 Run Automated Tests

```bash
cd backend
.venv/bin/pytest tests/
```
