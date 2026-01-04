# 🔍 Multi-Agent Market Research Engine

> **Autonomous AI-powered market research with hybrid intelligence: LLM + Deterministic Code**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-green.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)

---

## 📖 Overview

This is a sophisticated, autonomous market research engine designed to **validate startup ideas** with rigorous depth. Unlike standard "wrapper" applications that simply prompt an LLM, this engine employs a **Hybrid Architecture** combining:

- **🤖 Generative AI** (Perplexity + Gemini) for creativity, synthesis, and research
- **⚙️ Deterministic Code** (Python) for math, verification, and data extraction

**Core Philosophy: "Trust but Verify"**
> The system does not rely on LLM hallucinations for critical metrics.

---

## ✨ Features

| Component | AI (LLM) | Real Code (Python) |
|-----------|----------|-------------------|
| Pain Point Discovery | ✅ Perplexity | ✅ VADER Sentiment Analysis |
| Source Verification | ✅ Perplexity | ✅ Domain Trust Scoring |
| Competitor Analysis | ✅ Perplexity | ✅ BeautifulSoup Scraping |
| Persona Creation | ✅ Gemini | - |
| Feature Prioritization | ✅ Gemini | ✅ RICE Algorithm |
| Financial Modeling | ✅ Gemini | ✅ Pandas Calculations |

---

## 🏗️ Architecture: Dual LLM + Recursive State Machine

### LLM Strategy
The engine uses **two specialized LLMs** for optimal performance:

| LLM | Use Case | Agents |
|-----|----------|--------|
| **Perplexity** (sonar-pro) | Research & fact-finding | Strategist, Critic, Infiltrator |
| **Gemini** (2.5-flash) | Analysis & synthesis | Anthropologist, Analyzer, Innovator, Auditor, PDF Compiler |

### Agent Pipeline
Built on **LangGraph** with stateful graph topology and **Verification Loops**:

```
┌─────────────┐     ┌─────────┐
│ Strategist  │────▶│  Critic │──┐
│  (Search)   │◀────│ (Verify)│  │ Loop if not verified
└─────────────┘     └─────────┘◀─┘
        │
        ▼
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ Infiltrator │────▶│Anthropologist│────▶│ Analyzer │
│(Competitors)│     │  (Personas)  │     │ (Matrix) │
└─────────────┘     └──────────────┘     └──────────┘
        │
        ▼
┌─────────────┐     ┌─────────┐
│  Innovator  │────▶│ Auditor │──┐
│ (Features)  │◀────│(Finance)│  │ Loop if LTV/CAC < 3
└─────────────┘     └─────────┘◀─┘
        │
        ▼
┌──────────────┐
│ PDF Compiler │
│   (Report)   │
└──────────────┘
```

---

## 🔧 Module Breakdown

### 1. **Strategist** + Sentiment Engine
- **Role:** Identifies raw market pain points
- **LLM:** Perplexity (web search)
- **Real Code:** VADER Sentiment Analysis
- **Logic:** Only problems with polarity < -0.3 (genuine anger) are promoted

### 2. **Critic** + Domain Scorer
- **Role:** Ruthless gatekeeper of facts
- **LLM:** Perplexity (verification)
- **Real Code:** Weighted Domain Scoring
- **Logic:** Trust scores (gov.in=10, inc42.com=7, reddit=4, default=2)

### 3. **Infiltrator** + Web Scraper
- **Role:** Competitive intelligence
- **LLM:** Perplexity (research)
- **Real Code:** BeautifulSoup scraping for pricing & dark patterns

### 4. **Anthropologist**
- **Role:** Creates India 1/2/3 user personas
- **LLM:** Gemini (empathetic profiling)

### 5. **Analyzer**
- **Role:** Builds competitive matrix
- **LLM:** Gemini (structured analysis)

### 6. **Innovator** + RICE Scorer
- **Role:** Proposes "Delta-4" product features
- **LLM:** Gemini (ideation)
- **Real Code:** RICE Framework
- **Formula:** `Score = (Reach × Impact × Confidence) / Effort`

### 7. **Auditor** + Financial Engine
- **Role:** Validates business viability
- **LLM:** Gemini (assumptions)
- **Real Code:** Pandas for 24-month P&L projection
- **Metrics:** LTV, CAC, Payback Period, LTV/CAC Ratio

### 8. **PDF Compiler**
- **Role:** Generates the "Team Bible" report
- **LLM:** Gemini (narrative synthesis)
- **Output:** Markdown report with all findings

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API Keys:
  - [Perplexity API](https://docs.perplexity.ai/) - for research
  - [Google AI Studio](https://aistudio.google.com/) - for Gemini
  - [Tavily API](https://tavily.com/) - for web search

### Installation

```bash
# Clone the repository
git clone https://github.com/Abhishek-M-29/Market-Researcher.git
cd Market-Researcher

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy example config
cp .env.example .env

# Edit .env with your API keys
```

**.env file:**
```env
# API Keys (ALL REQUIRED)
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Model Settings
PERPLEXITY_MODEL=sonar-pro
GEMINI_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7
```

### Run the App

```bash
# Start Streamlit UI
streamlit run app.py

# Or use CLI
python main.py
```

Visit **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
Market Researcher/
├── src/
│   ├── agents/           # 8 Agent modules
│   │   ├── strategist.py     # Pain point discovery
│   │   ├── critic.py         # Verification & scoring
│   │   ├── infiltrator.py    # Competitor scraping
│   │   ├── anthropologist.py # Persona creation
│   │   ├── analyzer.py       # Competitive matrix
│   │   ├── innovator.py      # Feature ideation + RICE
│   │   ├── auditor.py        # Financial modeling
│   │   └── pdf_compiler.py   # Report generation
│   │
│   ├── graph/            # LangGraph workflow
│   │   ├── state.py          # MarketState TypedDict
│   │   └── workflow.py       # StateGraph + conditional loops
│   │
│   ├── utils/            # Deterministic Python modules
│   │   ├── llm.py            # Dual LLM config (Perplexity + Gemini)
│   │   ├── sentiment.py      # VADER sentiment analysis
│   │   ├── scoring.py        # Domain trust scoring
│   │   ├── financials.py     # Pandas financial modeling
│   │   ├── rice.py           # RICE feature prioritization
│   │   └── scraper.py        # BeautifulSoup web scraper
│   │
│   ├── tools/            # LangChain tools
│   │   └── search.py         # Tavily search wrapper
│   │
│   └── config/           # Configuration
│       ├── settings.py       # API keys & constants
│       └── prompts.py        # System prompts for agents
│
├── app.py                # Streamlit UI entry point
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore (protects .env)
└── README.md             # This file
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Orchestration** | LangGraph (Python) |
| **Research LLM** | Perplexity API (sonar-pro) |
| **Analysis LLM** | Google Gemini (2.5-flash) |
| **Web Search** | Tavily API |
| **Sentiment** | VADER Sentiment |
| **Scraping** | BeautifulSoup4, Requests |
| **Data** | Pandas |
| **UI** | Streamlit |

---

## 📊 Sample Output

When you run research on "AI-powered expense tracker for Indian freelancers", the engine:

1. **Finds pain points** from Reddit, Twitter, Quora with sentiment analysis
2. **Verifies claims** with statistics from trusted sources (gov.in, inc42.com)
3. **Scrapes competitors** like Expensify, Zoho Expense, Fyle
4. **Creates personas** for India 1 (Premium), India 2 (Aspirational), India 3 (Budget)
5. **Ranks features** using RICE (Quick Wins, Big Bets, Maybes, Ice Box)
6. **Models financials** with LTV/CAC ratio, payback period, 24-month projections
7. **Generates report** with actionable recommendations

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for stateful AI orchestration
- [Perplexity AI](https://perplexity.ai) for research-grade search
- [Google Gemini](https://deepmind.google/technologies/gemini/) for analytical capabilities
- [Streamlit](https://streamlit.io) for rapid UI development

---

**Built with ❤️ using LangGraph, Perplexity, Gemini, and deterministic Python logic.**
