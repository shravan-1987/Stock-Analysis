import os
from pathlib import Path

# --- DIRECTORY CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
ANNUAL_REPORTS_DIR = DATA_DIR / "annual_reports"
CACHE_DIR = DATA_DIR / "cache"

# Ensure directories exist
ANNUAL_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# --- CONSENSUS 6-PILLAR WEIGHTS (%) ---
# Total sums exactly to 1.00 (100%)
PILLAR_WEIGHTS = {
    "financial_health": 0.15,           # Pillar 1: Financial Health & Balance Sheet Strength (15%)
    "growth_momentum": 0.15,            # Pillar 2: Growth Momentum & Reinvestment Quality (15%)
    "moat_market_share": 0.24,          # Pillar 3: Market Size, Market Share & Competitive Moat (24%)
    "management_governance": 0.24,      # Pillar 4: Management Quality, Governance & Forensics (24%)
    "longevity_survival": 0.08,         # Pillar 5: 10-Year Longevity & Disruption Risk (8%)
    "valuation_margin_of_safety": 0.14  # Pillar 6: Valuation & Margin of Safety (14%)
}

# --- KNOCK-OUT / VETO SAFETY RULE THRESHOLDS ---
# If Governance or Longevity fall below these thresholds, overall score is capped
KNOCKOUT_THRESHOLDS = {
    "min_governance_score": 3.5,        # Trigger if Pillar 4 < 3.5 / 10
    "min_longevity_score": 3.0,         # Trigger if Pillar 5 < 3.0 / 10
    "max_capped_overall_score": 4.0     # Maximum overall score possible under Knock-Out Veto
}

# --- QUANTITATIVE BENCHMARKS FOR SCORING ---
BENCHMARKS = {
    "roce_high_target": 20.0,           # Sustained ROCE > 20% gets top scores
    "roce_mid_target": 15.0,            # Sustained ROCE > 15% is healthy benchmark
    "debt_to_equity_safe": 0.5,         # D/E < 0.5 is safe; > 1.5 is risky
    "interest_coverage_safe": 5.0,      # EBIT / Interest > 5x is safe
    "cfo_to_pat_healthy": 0.8,          # CFO / Net Profit > 80% shows strong cash conversion
    "peg_ratio_cheap": 1.0,             # PEG < 1.0 indicates margin of safety
    "peg_ratio_expensive": 3.0,         # PEG > 3.0 indicates overvaluation
    "max_promoter_pledging": 0.0        # Ideal promoter pledging is exactly 0.0%
}

# --- REQUESTS / USER AGENT CONFIGURATION ---
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT_SECONDS = 15
