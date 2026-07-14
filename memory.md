# Stock Analysis Project: Memory & Milestone Log

This document serves as the persistent historical log and architecture decision record (`ADR`) for the **Stock Analysis** project (`Stock-Analysis`), an automated AI-powered fundamental and forensic stock evaluation engine for Indian equities (NSE/BSE).

---

## 1. Project Overview & Mission
- **Target Location**: `C:\Users\Shravan Goyal\Antigravity Projects\Stock-Analysis`
- **GitHub Repository**: `shravan-1987/Stock-Analysis`
- **Core Mission**: Input any Indian stock ticker or name (e.g., `RELIANCE`, `TCS`), automatically scrape its last **3 years of Annual Report PDFs** (`Screener.in`) and **10-year quantitative financials** (`yfinance` + Screener tables), run deep document understanding with **Gemini 3.1 Pro**, and output an executive **10-Point Health & Longevity Scorecard** across 6 Core Pillars.

---

## 2. Key Architecture Decisions & Consensus Framework

### A. The Consensus 6-Pillar Evaluation Framework & Weights
On July 14, 2026, we finalized the scoring architecture by merging user-emphasized priorities (Heavy focus on Moat & Management Governance accounting for **48%** total weight) with AI-recommended external macro/disruption checks (**8%** Longevity weight):

| Pillar Number & Name | Weight (%) | Rationale / Key Variables |
|---|:---:|---|
| **1. Financial Health & Balance Sheet** | **15%** | Solvency, ROCE (>15% benchmark), Debt/Equity, and CFO/Net Profit cash conversion quality. |
| **2. Growth Momentum & Reinvestment** | **15%** | 3-Yr & 5-Yr Sales/EBITDA CAGR, operating leverage, and capital reinvestment (`Capex/CFO`). |
| **3. Market Size, Share & Competitive Moat** | **24%** | Industry TAM headroom, relative market share trend, pricing power, brand, and switching costs. |
| **4. Management Governance & Forensics** | **24%** | **Highest importance.** Promoter shareholding/pledging (`>0% is penalized`), Related Party Transactions (`RPTs`), Auditor qualifications, and contingent liabilities. |
| **5. 10-Year Longevity & Disruption Risk** | **8%** | External structural checks: AI/Tech disruption, green transition, regulatory bans, and concentration risks. |
| **6. Valuation & Margin of Safety** | **14%** | Historical P/E and P/BV medians, PEG Ratio (`P/E divided by 3-Yr Earnings CAGR < 1`), and FCF Yield. |
| **TOTAL** | **100%** | **Final Weighted Average Score out of 10.0** |

### B. The Knock-Out / Veto Safety Rule
To protect against value traps or fraudulent accounting:
- If **Pillar 4 (Management Governance)** scores below **3.5 / 10** (e.g., severe pledging > 50%, audit qualifications, massive unexplained RPTs), OR
- If **Pillar 5 (Longevity)** scores below **3.0 / 10** (e.g., terminal obsolescence or imminent regulatory ban),
- **The Overall Company Score is automatically capped at 4.0 / 10 (Avoid / Sell)** regardless of financial growth or cheap valuation.

---

## 3. Chronological Milestone Log

### [2026-07-14] - Phase 1: Ideation, Consensus Alignment & Repo Initialization
- Created parent folder `Antigravity Projects` at `C:\Users\Shravan Goyal\Antigravity Projects`.
- Drafted initial 5-Pillar ideation plan (`implementation_plan.md`) and expanded to exhaustive 6-Pillar framework upon user review.
- Conducted Weightage Calibration exercise: Aligned on consensus formula (**15% - 15% - 24% - 24% - 8% - 14%**) preserving user's 50% emphasis on Moat + Governance while incorporating standalone AI/Disruption checks.
- Formulated `task.md` execution checklist.
- Created `Stock-Analysis` directory inside `Antigravity Projects`, initialized Git repository, and logged in via GitHub CLI (`shravan-1987`).
- Created `memory.md` (this file) to record project history and architecture decisions.

---

## 4. Current Status & Next Action Items
- [x] Project workspace created and git initialized.
- [x] `memory.md` created.
- [ ] Create folder scaffolding (`data/annual_reports/`, `src/scrapers/`, `src/extractors/`, `src/engine/`, `src/utils/`).
- [ ] Create `requirements.txt` and `.gitignore`.
- [ ] Create remote GitHub repo (`gh repo create Stock-Analysis --public --source=. --remote=origin`) and push initial commit.
