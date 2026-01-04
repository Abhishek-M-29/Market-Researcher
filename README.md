# Multi-Agent Market Research Engine (2026 Edition)

## **Overview**
This project is a sophisticated, autonomous market research engine designed to validate startup ideas with rigorous depth. Unlike standard "wrapper" applications that simply prompt an LLM, this engine employs a **Hybrid Architecture** combining generative AI with deterministic code (Financial Modeling, Sentiment Analysis, and Scraping) to produce actionable, statistically backed business intelligence.

## **Core Philosophy**
**"Trust but Verify."**
The system does not rely on LLM hallucinations for critical metrics. It uses:
*   **AI** for creativity, synthesis, and empathy (Personas, Ideation).
*   **Code** for math, verification, and data extraction (Financials, Sentiment, Scoring).

---

## **System Architecture: The Recursive State Machine**
The engine is built on **LangGraph**, utilizing a stateful graph topology that allows for "Verification Loops." Agents can reject the work of previous agents and force a retry if quality standards are not met.

### **The Flow**
1.  **Strategist** (Search) $\rightarrow$ **Critic** (Verify)
    *   *Loop:* If verification fails, return to Strategist.
2.  **Infiltrator** (Competitor Intel) $\rightarrow$ **Anthropologist** (Personas) $\rightarrow$ **Analyzer** (Matrix)
3.  **Innovator** (Feature Ideation) $\rightarrow$ **Auditor** (Financial Viability)
    *   *Loop:* If financial viability (LTV/CAC) is low, return to Innovator to simplify.
4.  **PDF Compiler** (Final Report)

---

## **Module Breakdown: Hybrid Intelligence**

### **1. The Strategist + Sentiment Engine**
*   **Role:** Identifies raw market pain points.
*   **The "Real Code" Upgrade:** Uses **VADER Sentiment Analysis** to calculate a "Rage Score" for every scraped Reddit/Twitter comment.
*   **Logic:** Only problems with a polarity score $< -0.5$ (genuine anger) are promoted. Mild inconveniences are discarded.

### **2. The Critic + Domain Scorer**
*   **Role:** The ruthless gatekeeper of facts.
*   **The "Real Code" Upgrade:** Implements a **Weighted Domain Scoring** algorithm.
*   **Logic:** Assigns trust scores to sources (Gov/Edu > Top Tier News > Blogs). Claims supported only by low-trust domains are automatically rejected.

### **3. The Infiltrator + Ground-Truth Scraper**
*   **Role:** Competitive intelligence and "Mystery Shopping."
*   **The "Real Code" Upgrade:** Uses **BeautifulSoup** to programmatically scrape competitor pricing pages and detect "Dark Patterns" (e.g., specific keywords like "Call to Cancel").

### **4. The Anthropologist**
*   **Role:** Creates detailed user personas (India 1, 2, 3 framework).
*   **Tech:** Pure Generative AI (Gemini) for empathetic profiling and behavioral prediction.

### **5. The Innovator + RICE Scorer**
*   **Role:** Proposes "Delta-4" product features.
*   **The "Real Code" Upgrade:** Implements the **RICE Framework** (Reach, Impact, Confidence, Effort).
*   **Logic:** $Score = (Reach \times Impact \times Confidence) / Effort$. Features are mathematically sorted by ROI, not just "coolness."

### **6. The Auditor + Financial Modeling Engine**
*   **Role:** Validates business viability.
*   **The "Real Code" Upgrade:** Uses **Pandas** to build a 24-month P&L projection.
*   **Logic:** Calculates exact Unit Economics (CAC, LTV, Payback Period) based on input assumptions.

---

## **Technical Stack**
*   **Orchestration:** LangGraph (Python)
*   **LLM:** Gemini 2.5 Flash (via LangChain)
*   **Search:** Tavily API
*   **Data Processing:** Pandas, NumPy
*   **NLP:** VADER Sentiment
*   **Scraping:** BeautifulSoup4, Requests
*   **Reporting:** ReportLab (PDF Generation)
*   **UI:** Streamlit (Interactive Dashboard)

## **Project Structure**
```text
Market Researcher/
├── src/
│   ├── agents/           # Agent Logic (Strategist, Critic, etc.)
│   ├── graph/            # StateGraph & Workflow Definitions
│   ├── tools/            # Custom Tools (Scraper, Calculator)
│   ├── utils/            # Helper Modules (Sentiment, Scoring)
│   └── config/           # Prompts & Settings
├── notebooks/            # Experimental Sandboxes
├── .env                  # API Keys
├── main.py               # CLI Entry Point
└── app.py                # Streamlit UI Entry Point
```
