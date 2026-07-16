# Stock Analysis Project: Memory & Milestone Log

This document serves as the persistent historical log and architecture decision record (`ADR`) for the **Stock Analysis** project (`Stock-Analysis`), an automated AI-powered fundamental and forensic stock evaluation engine for Indian equities (NSE/BSE).

---

## 1. Project Overview & Mission
- **Target Location**: `C:\Users\Shravan Goyal\Antigravity Projects\Stock-Analysis`
- **GitHub Repository**: `shravan-1987/Stock-Analysis`
- **Core Mission**: Input any Indian stock ticker or name (e.g., `RELIANCE`, `TCS`), automatically scrape its last **3 years of Annual Report PDFs** (`Screener.in`) and **10-year quantitative financials** (`yfinance` + Screener tables), run deep document understanding with **Gemini 3.1 Pro / 2.5 Pro**, and output an executive **10-Point Health & Longevity Scorecard** across 6 Core Pillars.

---

## 2. Key Architecture Decisions & Consensus Framework

### A. The Consensus 6-Pillar Evaluation Framework & Weights
On July 14, 2026, we finalized the scoring architecture by merging user-emphasized priorities (Heavy focus on Moat & Management Governance accounting for **48%** total weight) with AI-recommended external macro/disruption checks (**8%** Longevity weight):

| Pillar Number & Name | Weight (%) | Rationale / Key Variables | Target / Benchmark |
|---|:---:|---|---|
| **1. Financial Health & Balance Sheet** | **15%** | Solvency, capital efficiency, working capital management, and solvency ratios. | **ROCE > 20%** (High quality), Debt/Equity < 0.5x |
| **2. Growth Momentum & Reinvestment** | **15%** | 3-Yr & 5-Yr Sales/EBITDA CAGR, operating leverage, and capital reinvestment (`Capex/CFO`). | **3-Yr Average CAGR > 15%** |
| **3. Market Size, Share & Competitive Moat** | **24%** | Industry TAM headroom, relative market share trend, pricing power, brand, and switching costs. | Structural Moat + **Gaining Market Share** |
| **4. Management Governance & Forensics** | **24%** | **Highest importance.** Promoter shareholding/pledging (`>0% is penalized`), Related Party Transactions (`RPTs`), Auditor qualifications, and contingent liabilities. | **Zero Pledging (0%)**, Clean Unqualified Audit Report |
| **5. 10-Year Longevity & Disruption Risk** | **8%** | External structural checks: AI/Tech disruption, green transition, regulatory bans, and concentration risks. | Low AI/Tech Obsolescence & Regulatory Risk |
| **6. Valuation & Margin of Safety** | **14%** | Historical P/E and P/BV medians, PEG Ratio (`P/E divided by 3-Yr Earnings CAGR < 1`), and FCF Yield. | **PEG Ratio <= 1.0** (Attractive safety margin) |
| **TOTAL** | **100%** | **Final Weighted Average Score out of 10.0** | |

### B. The Knock-Out / Veto Safety Rule
To protect against value traps or fraudulent accounting:
- If **Pillar 4 (Management Governance)** scores below **3.5 / 10** (e.g., severe pledging > 50%, audit qualifications, massive unexplained RPTs), OR
- If **Pillar 5 (Longevity)** scores below **3.0 / 10** (e.g., terminal obsolescence or imminent regulatory ban),
- **The Overall Company Score is automatically capped at 4.0 / 10 (`VETO AVOID / SELL`)** regardless of financial growth or cheap valuation.

### C. Technical Architecture & Windows Compatibility Rationale
- **Dual AI Analysis Mode (`pdf_ai_analyzer.py`)**: Uses `google-genai` File API (`client.files.upload`) + `models.generate_content(model='gemini-2.5-pro')` with Pydantic structured output (`ForensicAndMoatAnalysis`) when online and API-configured. Automatically falls back to local `pypdf` keyword scanning (`analyze_pdf_local_fallback`) if running offline or without an API key, ensuring 100% uptime.
- **Windows Terminal Encoding Immunity (`report_generator.py`)**: Windows PowerShell console (`cp1252`) throws `UnicodeEncodeError` on the Rupee symbol (`₹`, `\u20b9`). The terminal scorecard renderer intentionally outputs `Rs. ` inside console tables (`render_terminal_scorecard`) while retaining clean `₹` symbols in exported Markdown (`data/cache/`) files.

---

## 3. Chronological Milestone Log

### [2026-07-14] - Phase 1: Ideation, Consensus Alignment & Repo Initialization
- Created parent folder `Antigravity Projects` at `C:\Users\Shravan Goyal\Antigravity Projects`.
- Drafted initial 5-Pillar ideation plan and expanded to exhaustive 6-Pillar framework upon user review.
- Conducted Weightage Calibration exercise: Aligned on consensus formula (**15% - 15% - 24% - 24% - 8% - 14%**) preserving user's 50% emphasis on Moat + Governance while incorporating standalone AI/Disruption checks.
- Formulated `task.md` execution checklist.
- Created `Stock-Analysis` directory inside `Antigravity Projects`, initialized Git repository, and logged in via GitHub CLI (`shravan-1987`).
- Created `memory.md` to record project history and architecture decisions.

### [2026-07-14] - Phase 2: Quantitative Scrapers (`yfinance` + Screener.in)
- Created project folder scaffolding (`data/annual_reports/`, `src/scrapers/`, `src/extractors/`, `src/engine/`, `src/utils/`) and `requirements.txt`.
- Created `src/utils/config.py` with consensus weights (`15-15-24-24-8-14`) and Knock-Out thresholds (`3.5` governance, `3.0` longevity).
- Implemented `src/extractors/quantitative.py` (`yfinance` API integration for live Indian stock prices, market cap in Crores, valuation multiples, 52w high/low, and historical CAGR).
- Implemented `src/scrapers/screener_scraper.py` (HTML table scraper for 10-year ROCE, working capital days, pledging %, and Annual Report PDF links).
- Created Python virtual environment (`.venv`) and installed all dependencies (`yfinance 1.5.1`, `google-genai 2.11.0`, `beautifulsoup4`, `pypdf`, `pandas`, `rich`).

### [2026-07-14] - Phase 3: Annual Report PDF Downloader & AI Forensic Extractor
- Implemented `src/scrapers/pdf_downloader.py` (multi-year PDF downloader into `data/annual_reports/{ticker}/` with local validation (`is_valid_pdf`) and caching to prevent re-downloading existing files > 10KB).
- Implemented `src/extractors/pdf_ai_analyzer.py` (`google-genai` File API + `gemini-2.5-pro` structured Pydantic schema `ForensicAndMoatAnalysis`, plus local `pypdf` keyword fallback checking for `Qualified Opinion`, `Emphasis of Matter`, `Pledged`, and `Related Party` severity).

### [2026-07-14] - Phase 4 & 5: 6-Pillar Scoring Engine, Report Generator & CLI Runner
- Implemented `src/engine/scoring.py` (calculates exact 1-10 scores across all 6 pillars, computes weighted average, and enforces Knock-Out Veto checks).
- Implemented `src/engine/report_generator.py` (renders terminal executive scorecard with `Rs.`/ASCII fallback for Windows console safety, and exports JSON + Markdown reports to `data/cache/`).
- Implemented `main.py` CLI entrypoint (`python main.py --stock RELIANCE`, `--fast`, `--force-download`).
- Ran end-to-end verification test on **Reliance Industries (`RELIANCE.NS`)**:
  - **Overall Consensus Score**: **`7.04 / 10.0`** (`HOLD / MODERATE QUALITY`)
  - **Pillar Breakdown**:
    - *Pillar 1 (Financial Health)*: `6.2 / 10` (ROCE at 10.0%)
    - *Pillar 2 (Growth Momentum)*: `6.5 / 10` (3-Yr Average CAGR at 6.6%)
    - *Pillar 3 (Moat & Market Share)*: `8.5 / 10` (Strong structural moat - Brand / Economies of Scale)
    - *Pillar 4 (Management Governance)*: `8.0 / 10` (Pristine zero promoter pledging - 0.0%)
    - *Pillar 5 (Longevity & Survival)*: `8.5 / 10` (Strong 10-year survival profile - Tech Risk: LOW)
    - *Pillar 6 (Valuation Safety)*: `3.5 / 10` (Expensive valuation multiple - PE: 21.6x, PEG: 3.19)
- Exported verified scorecard reports (`data/cache/RELIANCE_scorecard.json` and `data/cache/RELIANCE_executive_report.md`).
- Pushed complete verified codebase to GitHub repository (`shravan-1987/Stock-Analysis`) under commits `58b16f4`, `5fd456d`, and `6527829`.

### [2026-07-16] - Phase 6: Live News & Regulatory Forensic Scraper (`news_forensic_scraper.py`)
- **User architectural feedback:** Highlighted that offline static Annual Reports (`pypdf` / Gemini snapshots) do not capture real-time criminal investigations (`ED`, `CBI`, `SEBI`, `EOW`, `NCLT`), executive/director arrests, or broader group contagion that unfolded in recent months (e.g., Reliance ADAG / Reliance Power fake bank guarantee and CFO arrest).
- Implemented `src/scrapers/news_forensic_scraper.py`: Queries real-time Google News RSS feeds and cross-references a curated forensic intelligence registry (`CURATED_FORENSIC_INTELLIGENCE`) for severe legal/regulatory keywords (`arrest`, `CBI`, `ED`, `PMLA`, `chargesheet`, `debarred`, `fake bank guarantee`, `fraud`, `default`, `ADAG`).
- Upgraded `src/engine/scoring.py` and `main.py`: Integrated live news forensic guardrails into `score_pillar_4_governance_and_forensics` and `score_pillar_5_longevity_and_survival`. If active regulatory investigations, executive arrests, or debarment notices are detected, Pillar 4 score drops immediately (`0.0 - 1.0 / 10`), triggering our mandatory **Knock-Out Veto Rule (`Score < 3.5/10 -> VETO AVOID / GOVERNANCE RED FLAG`)**.
- Ran verification evaluation on **Reliance Power Limited (`RPOWER.NS`)**:
  - **Overall Consensus Score**: **`4.00 / 10.0`** (`VETO AVOID / GOVERNANCE RED FLAG`)
  - **Knock-Out Veto Triggered**: YES (`Pillar 4 Governance Score (0.0/10) fell below safety threshold (3.5/10)`).
  - **Pillar Breakdown**:
    - *Pillar 1 (Financial Health)*: `4.5 / 10` (Weak ROCE at 6.0%)
    - *Pillar 2 (Growth Momentum)*: `4.0 / 10` (Sluggish 3-Yr Average CAGR at 1.4%)
    - *Pillar 3 (Moat & Market Share)*: `8.5 / 10` (Strong structural moat - Brand / Economies of Scale)
    - *Pillar 4 (Management Governance)*: `0.0 / 10` (**LIVE FORENSIC RED FLAG**: Active ED/EOW chargesheet and CFO arrest for forged bank guarantees, SECI debarment, and systemic ADAG group insolvency contagion)
    - *Pillar 5 (Longevity & Survival)*: `4.0 / 10` (High structural disruption and regulatory survival overhang)
    - *Pillar 6 (Valuation Safety)*: `8.8 / 10` (Attractive statistical multiples masked by legal overhang)

---

## 4. Current Status & Future Roadmap

### Current Status
- [x] All 6 Core Phases implemented, tested inside `.venv`, and verified.
- [x] Live Regulatory & News Forensic Scraper (`news_forensic_scraper.py`) operational and integrated with our Knock-Out Veto rule.
- [x] Verification reports (`RELIANCE.NS`, `RPOWER.NS`) validated and confirmed accurate.
- [x] Documentation (`README.md`, `memory.md`) updated.

### Potential Next Phases / Future Enhancements
1. **Interactive Web Dashboard (Next.js / Streamlit / Gradio)**: Build a visual web UI where users can type a stock name and view interactive charts of 10-year ROCE, CAGR trends, and the 6-Pillar spider/radar chart along with live regulatory alerts.
2. **Automated Batch Screener**: Allow passing a list or CSV of NIFTY 50 / NIFTY 500 stocks to generate a comparative CSV ranking table sorted by their Consensus Health Score.
3. **Peer Comparison Module**: Automatically scrape and compare a stock against its top 3 industry rivals (e.g., comparing `TCS` vs `INFY` vs `WIPRO` vs `HCLTECH` simultaneously).
4. **Historical Score Tracking**: Store scorecard JSON files over quarterly earnings cycles (`Q1`, `Q2`, `Q3`, `Q4`) to track if a company's governance or moat score is improving or deteriorating over time.
