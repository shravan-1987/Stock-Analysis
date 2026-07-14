# Indian Stock Analysis & Evaluation Engine (`Stock-Analysis`)

An automated AI-powered fundamental and forensic stock evaluation engine specifically tailored for **Indian Equities (NSE / BSE)**.

## Overview
This engine automatically fetches and analyzes:
1. **Last 3 Years of Annual Report PDFs** (from `Screener.in`)
2. **10-Year Quantitative Financial Tables** (from `yfinance` & Screener.in)
3. **Forensic & Governance Footnotes** (using **Gemini 3.1 Pro** Deep Document Understanding)

And outputs an executive **10-Point Health & Longevity Scorecard** across **6 Core Pillars**:
1. **Financial Health & Balance Sheet Strength** (`15%`)
2. **Growth Momentum & Reinvestment Quality** (`15%`)
3. **Market Size, Market Share & Competitive Moat** (`24%`)
4. **Management Quality, Corporate Governance & Forensics** (`24%`)
5. **10-Year Longevity & Disruption Risk** (`8%`)
6. **Valuation & Margin of Safety** (`14%`)

### Safety Mechanism
Includes a **Knock-Out / Veto Rule**: If Management Governance scores `< 3.5/10` (promoter pledging > 50%, fraud, auditor qualifications) or Longevity scores `< 3.0/10`, the overall company score is capped at `4.0/10 (Avoid/Sell)` regardless of growth or cheap valuation.

---

## Directory Structure
```
Stock-Analysis/
├── data/annual_reports/      # Downloaded Annual Report PDFs cached locally
├── src/
│   ├── scrapers/             # Screener.in PDF downloader & table extractor
│   ├── extractors/           # yfinance ratios & Gemini 3.1 Pro PDF analyzer
│   ├── engine/               # 6-Pillar scoring engine & Knock-Out rule
│   └── utils/                # Configuration and threshold definitions
├── memory.md                 # Persistent project log & architecture decisions
└── main.py                   # CLI entrypoint (`python main.py --stock RELIANCE`)
```
