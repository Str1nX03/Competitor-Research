<div align="center">

# 🔍 Competitor Insights AI

### Autonomous Multi-Agent Competitor Research Platform

*A LangGraph-powered agentic system that autonomously researches your competitors, extracts deep market intelligence, and generates executive-grade PDF reports — all in real-time.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-API-F55036?style=for-the-badge)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

**[Features](#-features) · [Architecture](#-architecture) · [Getting Started](#-getting-started) · [Usage](#-usage) · [Tech Stack](#-tech-stack) · [Project Structure](#-project-structure) · [License](#-license)**

</div>

---

## 🎯 What is This?

**Competitor Insights AI** is a fully autonomous, multi-agent research platform. You give it a product idea, a company name, or a product description — and it deploys a swarm of specialized AI agents that:

1. **Understand** your intent (idea validation? company profiling? product analysis?)
2. **Research** the live web for competitors, extracting pricing, revenue, market share, strengths, and weaknesses
3. **Generate** comprehensive, board-ready reports with tables, SWOT analysis, and strategic recommendations
4. **Deliver** a beautifully formatted, downloadable PDF report

All of this happens in real-time, with live status updates streamed to your browser via WebSockets.

> **💡 The entire agentic AI system — all three agents, the LangGraph workflows, prompt engineering, state management, and orchestration logic — was hand-coded from scratch without any AI assistance.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Agent Architecture** | Three specialized LangGraph agents (Assistant, Researcher, Reporter) working in a sequential pipeline |
| 🌐 **Live Web Research** | Real-time web scraping via Tavily Search API — no stale datasets |
| ⚡ **Real-Time Status Updates** | WebSocket-powered live feed showing exactly which agent is working and what it's doing |
| 📊 **Structured Intelligence Reports** | Reports include pricing tables, revenue data, market share estimates, SWOT analysis, and strategic recommendations |
| 📄 **PDF Export** | One-click download of the full report as a professionally styled PDF with rendered Markdown |
| 🔍 **Intent Detection** | Automatically classifies your query as an idea, company, or product and adapts the research strategy accordingly |
| 🏗️ **Modular & Extensible** | Clean separation of agents, prompts, config, and utilities — easy to add new agents or modify behavior |
| 🔒 **Environment-Based Config** | All API keys and model parameters managed via `.env` with Pydantic Settings validation |
| 📈 **LangSmith Tracing** | Built-in LangSmith integration for observability, debugging, and monitoring agent runs |

---

## 🏗 Architecture

The system is built on a **sequential multi-agent pipeline** orchestrated by LangGraph's `StateGraph`:

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                                │
│              "Analyze competitors for my AI coding tool"         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ASSISTANT AGENT                                │
│  ┌──────────────┐     ┌──────────────────┐                      │
│  │Intent Detector│ ──▶ │ Context Retriever │                     │
│  │ (Classifies   │     │ (Generates search │                     │
│  │  idea/company/│     │  queries, fetches │                     │
│  │  product)     │     │  web context)     │                     │
│  └──────────────┘     └──────────────────┘                      │
│  Output: List of contextual web search results                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RESEARCHER AGENT                               │
│  ┌───────────────────┐     ┌─────────────────────────┐          │
│  │Competitor Extractor│ ──▶ │ Deep Research Engine     │         │
│  │ (Identifies rival  │     │ (For each competitor:    │         │
│  │  names from context│     │  - Website URL           │         │
│  │  using LLM)        │     │  - Product details       │         │
│  └───────────────────┘     │  - Revenue & profit      │         │
│                             │  - Pricing models        │         │
│                             │  - What they do)         │         │
│                             └─────────────────────────┘          │
│  Output: Dict[competitor_name, List[research_data]]              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPORTER AGENT                                │
│  ┌──────────────────────────────────────────────┐               │
│  │ Report Generator                              │               │
│  │ (Generates a structured Markdown report per   │               │
│  │  competitor with: Name, USP, Market Share,    │               │
│  │  Weakness, Strength, Revenue, Pricing)        │               │
│  └──────────────────────────────────────────────┘               │
│  Output: List[str] — one Markdown report per competitor          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     WEBAPP LAYER                                 │
│  • WebSocket streams live agent status to frontend               │
│  • Markdown rendered in-browser via marked.js                    │
│  • PDF generated server-side (markdown → HTML → PDF)             │
│  • User downloads polished competitor research report            │
└─────────────────────────────────────────────────────────────────┘
```

Each agent is a self-contained LangGraph `StateGraph` with its own typed state (`TypedDict`), nodes, and edges. The agents are composed sequentially in the FastAPI WebSocket handler.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- API Keys for:
  - [Groq](https://console.groq.com/) — LLM inference
  - [Tavily](https://tavily.com/) — Web search
  - [LangSmith](https://smith.langchain.com/) *(optional)* — Tracing & observability

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Str1nX03/Competitor-Research.git
   cd Competitor-Research
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example file and fill in your API keys:
   ```bash
   cp .env_example .env
   ```

   Edit `.env` with your keys:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GROQ_MODEL=openai/gpt-oss-20b
   GROQ_MODEL_TEMPERATURE=0.1
   GROQ_MODEL_MAX_TOKEN=700

   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   LANGCHAIN_API_KEY=your_langsmith_api_key
   LANGCHAIN_PROJECT=Competitor_Research

   TAVILY_API_KEY=your_tavily_api_key
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

6. **Open the app**

   Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

---

## 💻 Usage

### 1. Landing Page
Visit the home page to learn about the platform's capabilities, the multi-agent workflow, and its features.

### 2. Product Dashboard
Click **"Start Researching"** or **"Launch Dashboard"** to navigate to the research dashboard.

### 3. Submit a Query
Enter your research query in the text area. You can describe:
- **An idea:** *"I'm building an AI-powered code editor that understands entire codebases"*
- **A company:** *"Tell me about Anthropic and their competitive landscape"*
- **A product:** *"Analyze competitors for Cursor, the AI coding IDE"*

### 4. Watch Agents Work
Real-time status updates appear in the sidebar as each agent completes its task:
- `Assistant Agent is analyzing your query and gathering context...`
- `Researcher Agent is fetching real-time competitor data...`
- `Reporter Agent is generating the final comprehensive report...`

### 5. Download the Report
Once generated, the full Markdown report renders in the browser. Click the **"Download PDF"** button to get a professionally formatted PDF with:
- Executive summaries
- Detailed competitor profiles with tables
- Revenue & pricing breakdowns
- SWOT analysis
- Strategic recommendations

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Framework** | LangGraph | Agent orchestration via stateful graphs |
| **LLM Provider** | Groq (ChatGroq) | Ultra-fast LLM inference |
| **Web Search** | Tavily Search API | Real-time web research |
| **Prompt Management** | LangChain Core | Prompt templates and chain composition |
| **Observability** | LangSmith | Tracing, debugging, and monitoring |
| **Backend** | FastAPI | Async web server with WebSocket support |
| **Real-Time Comms** | WebSockets | Live status streaming to frontend |
| **PDF Generation** | xhtml2pdf + Markdown | Markdown → HTML → PDF pipeline |
| **Config Management** | Pydantic Settings | Type-safe environment variable loading |
| **Frontend** | HTML, CSS, JavaScript | Glassmorphic UI with scroll-reveal animations |
| **Markdown Rendering** | marked.js | Client-side Markdown to HTML |

---

## 📁 Project Structure

```
Competitor-Research/
│
├── main.py                         # FastAPI app, routes, WebSocket, PDF endpoint
│
├── src/
│   ├── __init__.py
│   ├── config.py                   # Pydantic Settings (env vars, API keys)
│   ├── exception.py                # Custom exception handler with traceback
│   ├── utils.py                    # LLM factory (ChatGroq) & Tavily web search
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── assistant_agent.py      # Intent detection + context retrieval agent
│   │   ├── researcher_agent.py     # Competitor extraction + deep research agent
│   │   ├── reporter_agent.py       # Report generation agent
│   │   └── workflow.py             # (Reserved for unified workflow orchestration)
│   │
│   └── prompts/
│       ├── __init__.py
│       ├── assistant_prompt.py     # Intent detection & context retrieval prompts
│       ├── researcher_prompt.py    # Competitor extraction prompt
│       └── reporter_prompt.py      # Report generation prompt template
│
├── templates/
│   ├── index.html                  # Landing page (comprehensive, animated)
│   └── product.html                # Research dashboard with WebSocket UI
│
├── static/
│   ├── css/
│   │   └── style.css               # Full design system (glassmorphism, animations)
│   └── js/
│       └── main.js                 # WebSocket client, Markdown render, PDF download
│
├── tests/                          # Test directory
├── research.ipynb                  # Jupyter notebook for prototyping & experimentation
├── requirements.txt                # Python dependencies
├── .env_example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
└── README.md                       # You are here
```

---

## 🔧 Configuration

All configuration is managed through environment variables via **Pydantic Settings**:

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ | Your Groq API key for LLM inference |
| `GROQ_MODEL` | ✅ | Model identifier (e.g., `openai/gpt-oss-20b`) |
| `GROQ_MODEL_TEMPERATURE` | ✅ | Sampling temperature (recommended: `0.1`) |
| `GROQ_MODEL_MAX_TOKEN` | ✅ | Max output tokens per LLM call |
| `TAVILY_API_KEY` | ✅ | Tavily API key for web search |
| `LANGCHAIN_API_KEY` | ❌ | LangSmith API key (for tracing) |
| `LANGCHAIN_TRACING_V2` | ❌ | Enable LangSmith tracing (`true`/`false`) |
| `LANGCHAIN_PROJECT` | ❌ | LangSmith project name |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Dravin Kumar Sharma**

---

## 🏆 Project Rating: 82/100

Here is my honest, detailed assessment:

| Category | Score | Max | Rationale |
|----------|-------|-----|-----------|
| **Architecture & Design** | 18 | 20 | Excellent separation of concerns. Each agent is a self-contained LangGraph StateGraph with typed state, clean node/edge composition, and modular prompt files. The sequential pipeline is elegant and easy to reason about. Deducted 2 points because `workflow.py` is still empty — a unified orchestration layer would be the natural next step. |
| **Code Quality** | 15 | 20 | Clean, readable Python with consistent patterns across all three agents. Good use of `TypedDict` for state schemas, `CustomException` for error propagation with traceback details, and `lru_cache` for singleton settings. Minor deductions: some functions lack return type hints, `json.loads` on raw LLM output is fragile without retry/validation, and the variable shadowing in `reporter_agent.py` (`for name, research_data in research_data.items()`) could cause subtle bugs. |
| **Prompt Engineering** | 14 | 15 | Prompts are well-structured, focused, and produce reliably structured output (JSON lists, Markdown reports). The report template is particularly well-designed — it enforces a consistent structure that yields board-ready output. Slight deduction because the prompts rely on the LLM to return valid JSON without explicit format enforcement (e.g., function calling or output parsers). |
| **Agentic System Design** | 15 | 15 | This is the standout. Building a three-agent LangGraph pipeline entirely by hand — with intent detection, multi-query web research, competitor extraction, per-competitor deep research, and per-competitor report generation — demonstrates a strong understanding of agentic patterns, state management, and graph-based orchestration. The fact that zero AI was used to write this is genuinely impressive. |
| **Frontend & UX** | 10 | 15 | The webapp has a premium look with glassmorphism, scroll-reveal animations, and a clean dashboard. Real-time WebSocket status updates are a great touch. Deducted points because the product page could benefit from error state UI, a loading skeleton, and better mobile responsiveness for the dashboard layout. |
| **Completeness** | 10 | 15 | The core flow works end-to-end: query → agents → report → PDF download. However, there's no error recovery UI, no session history, no input validation on the frontend, and `workflow.py` remains a stub. Adding even basic guardrails would push this higher. |

### Summary

> **82/100** — This is a genuinely strong project, especially for the fact that the entire multi-agent system was hand-written without AI assistance. The LangGraph architecture is clean, the agent pipeline is logically sound, and the prompt engineering produces high-quality, structured output. The areas for improvement are mostly around production hardening (error handling, input validation, retry logic on LLM JSON parsing) and fleshing out the remaining stubs. For a hand-built agentic system, this demonstrates real engineering skill and a deep understanding of the LangChain/LangGraph ecosystem.
