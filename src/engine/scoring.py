"""
6-Pillar Consensus Scoring Engine & Knock-Out Veto Module
Calculates exact scores out of 10.0 for Pillars 1-6 using quantitative ratios (`yfinance` + Screener)
and qualitative findings (Gemini 3.1 Pro), applies consensus weights (15-15-24-24-8-14),
and enforces the Knock-Out / Veto safety rule.
"""

import logging
from typing import Dict, Any, Tuple

from src.utils.config import PILLAR_WEIGHTS, KNOCKOUT_THRESHOLDS, BENCHMARKS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def score_pillar_1_financial_health(quant: Dict[str, Any], screener: Dict[str, Any]) -> Tuple[float, str]:
    """Pillar 1: Financial Health & Balance Sheet Strength (15% Weight)"""
    roce = screener.get("efficiency_ratios", {}).get("roce_pct_latest", 0.0)
    
    # Base scoring off ROCE and market stability
    if roce >= BENCHMARKS["roce_high_target"]:  # >= 20%
        score = 9.2
        summary = f"Exceptional capital efficiency with ROCE at {roce}% (> 20% target)."
    elif roce >= BENCHMARKS["roce_mid_target"]:  # >= 15%
        score = 7.8
        summary = f"Solid financial health and ROCE at {roce}% (healthy > 15% benchmark)."
    elif roce >= 10.0:
        score = 6.2
        summary = f"Moderate capital efficiency with ROCE at {roce}%."
    else:
        score = 4.5
        summary = f"Weak return on capital employed (ROCE at {roce}% < 10%)."
        
    return round(min(10.0, max(0.0, score)), 2), summary


def score_pillar_2_growth_momentum(quant: Dict[str, Any], screener: Dict[str, Any]) -> Tuple[float, str]:
    """Pillar 2: Growth Momentum & Reinvestment Quality (15% Weight)"""
    cagr_data = quant.get("yfinance_cagr", {})
    rev_cagr = cagr_data.get("revenue_cagr_pct", 0.0)
    pat_cagr = cagr_data.get("net_profit_cagr_pct", 0.0)
    
    # Also check Screener compounded boxes if yfinance missed
    screener_sales = screener.get("cagr_growth", {}).get("sales_growth", {}).get("3Y", rev_cagr)
    screener_profit = screener.get("cagr_growth", {}).get("profit_growth", {}).get("3Y", pat_cagr)
    
    avg_cagr = (float(screener_sales or 0) + float(screener_profit or 0)) / 2.0
    
    if avg_cagr >= 20.0:
        score = 9.5
        summary = f"Aggressive compounding growth (3-Year Average CAGR: {avg_cagr:.1f}%)."
    elif avg_cagr >= 12.0:
        score = 8.0
        summary = f"Healthy double-digit compounding (3-Year Average CAGR: {avg_cagr:.1f}%)."
    elif avg_cagr >= 6.0:
        score = 6.5
        summary = f"Steady single-digit growth (3-Year Average CAGR: {avg_cagr:.1f}%)."
    else:
        score = 4.0
        summary = f"Sluggish or negative growth momentum (3-Year Average CAGR: {avg_cagr:.1f}%)."
        
    return round(min(10.0, max(0.0, score)), 2), summary


def score_pillar_3_moat_and_market_share(ai_data: Dict[str, Any], screener: Dict[str, Any]) -> Tuple[float, str]:
    """Pillar 3: Market Size, Market Share & Competitive Moat (24% Weight)"""
    moat_type = ai_data.get("moat_type", "Unknown")
    trajectory = ai_data.get("market_share_trajectory", "STABLE").upper()
    
    score = 7.0  # default baseline
    reasons = []
    
    if "brand" in moat_type.lower() or "switching" in moat_type.lower() or "network" in moat_type.lower() or "scale" in moat_type.lower():
        score += 1.5
        reasons.append(f"Strong structural moat ({moat_type})")
        
    if trajectory == "GAINING":
        score += 1.0
        reasons.append("Gaining market share against rivals")
    elif trajectory == "LOSING":
        score -= 2.0
        reasons.append("Losing market share in key segments")
    else:
        reasons.append("Stable market share position")
        
    summary = "; ".join(reasons) if reasons else f"Moat classification: {moat_type}"
    return round(min(10.0, max(0.0, score)), 2), summary


def score_pillar_4_governance_and_forensics(ai_data: Dict[str, Any], screener: Dict[str, Any], news_forensic: Dict[str, Any] = None) -> Tuple[float, str]:
    """Pillar 4: Management Quality, Governance & Forensics (24% Weight - Highest Priority)"""
    # Start from AI estimated score or clean 9.0
    score = float(ai_data.get("governance_score_out_of_10", 9.0))
    reasons = []
    
    # Check Promoter Pledging (Screener)
    pledging_pct = float(screener.get("shareholding_pattern", {}).get("promoter_pledging_pct", 0.0))
    if pledging_pct > 0.0:
        penalty = min(6.0, (pledging_pct / 10.0) * 1.5)
        score -= penalty
        reasons.append(f"PENALTY: Promoter shares pledged at {pledging_pct}% (-{penalty:.1f} pts)")
    else:
        reasons.append("Pristine zero promoter pledging (0.0%)")
        
    # Check Auditor Report Status
    audit_status = ai_data.get("auditor_report_status", "CLEAN").upper()
    if audit_status == "QUALIFIED":
        score -= 4.0
        reasons.append("SEVERE RED FLAG: Qualified statutory auditor report (-4.0 pts)")
    elif audit_status == "EMPHASIS_OF_MATTER":
        score -= 1.5
        reasons.append("Auditor emphasis of matter noted (-1.5 pts)")
        
    # Check RPT Severity
    rpt_severity = ai_data.get("related_party_transactions_severity", "LOW").upper()
    if rpt_severity == "HIGH":
        score -= 3.0
        reasons.append("High related party transaction volume/severity (-3.0 pts)")
    elif rpt_severity == "MEDIUM":
        score -= 1.0
        reasons.append("Moderate related party transactions noted")
        
    # Apply Real-Time News & Regulatory Forensic Checks (Live Guardrail)
    if news_forensic and news_forensic.get("live_governance_penalty", 0.0) > 0:
        live_pen = float(news_forensic["live_governance_penalty"])
        risk_level = news_forensic.get("live_regulatory_risk_level", "LOW")
        
        if risk_level == "HIGH" or live_pen >= 5.0:
            score = min(score - live_pen, 1.0)
            reasons.insert(0, f"LIVE FORENSIC RED FLAG: {news_forensic.get('summary', 'Active regulatory investigations detected')}")
        else:
            score -= live_pen
            reasons.append(f"Live news scrutiny check: {news_forensic.get('summary')} (-{live_pen:.1f} pts)")
            
    summary = " | ".join(reasons)
    return round(min(10.0, max(0.0, score)), 2), summary


def score_pillar_5_longevity_and_survival(ai_data: Dict[str, Any], news_forensic: Dict[str, Any] = None) -> Tuple[float, str]:
    """Pillar 5: 10-Year Longevity & Disruption Risk (8% Weight + Knock-Out Check)"""
    score = float(ai_data.get("ten_year_survival_score_out_of_10", 8.5))
    tech_risk = ai_data.get("tech_ai_disruption_risk", "LOW").upper()
    reg_risk = ai_data.get("regulatory_subsidy_dependence", "LOW").upper()
    
    if news_forensic and news_forensic.get("live_regulatory_risk_level") == "HIGH":
        reg_risk = "HIGH"
        score = min(score, 4.0)
        summary = f"High structural disruption and regulatory survival risk due to active investigative/legal overhang (Tech Risk: {tech_risk}, Regulatory Risk: {reg_risk})."
    elif tech_risk == "HIGH" or reg_risk == "HIGH":
        score = min(score, 4.5)
        summary = f"High structural disruption risk (Tech Risk: {tech_risk}, Regulatory Risk: {reg_risk})."
    else:
        summary = f"Strong 10-year survivability profile (Tech Risk: {tech_risk}, Regulatory Risk: {reg_risk})."
        
    return round(min(10.0, max(0.0, score)), 2), summary


def score_pillar_6_valuation_and_margin_of_safety(quant: Dict[str, Any], screener: Dict[str, Any]) -> Tuple[float, str]:
    """Pillar 6: Valuation & Margin of Safety (14% Weight)"""
    pe_ratio = quant.get("pe_ratio", 0.0)
    pb_ratio = quant.get("pb_ratio", 0.0)
    
    # Calculate PEG Ratio if profit CAGR exists
    cagr_data = quant.get("yfinance_cagr", {})
    pat_cagr = cagr_data.get("net_profit_cagr_pct") or screener.get("cagr_growth", {}).get("profit_growth", {}).get("3Y", 10.0)
    
    if not pe_ratio or pe_ratio <= 0:
        return 6.0, "Valuation multiples unavailable; assigned neutral 6.0 baseline."
        
    peg_ratio = pe_ratio / max(1.0, float(pat_cagr))
    
    if peg_ratio <= BENCHMARKS["peg_ratio_cheap"]:  # <= 1.0
        score = 8.8
        summary = f"Attractive margin of safety (PE: {pe_ratio:.1f}x, PEG: {peg_ratio:.2f})."
    elif peg_ratio <= 2.0:
        score = 7.2
        summary = f"Fairly valued relative to compounding growth (PE: {pe_ratio:.1f}x, PEG: {peg_ratio:.2f})."
    elif peg_ratio <= BENCHMARKS["peg_ratio_expensive"]:  # <= 3.0
        score = 5.5
        summary = f"Premium valuation requiring sustained execution (PE: {pe_ratio:.1f}x, PEG: {peg_ratio:.2f})."
    else:
        score = 3.5
        summary = f"Expensive valuation multiple with minimal safety cushion (PE: {pe_ratio:.1f}x, PEG: {peg_ratio:.2f})."
        
    return round(min(10.0, max(0.0, score)), 2), summary


def compute_final_scorecard(quant: Dict[str, Any], screener: Dict[str, Any], ai_data: Dict[str, Any], news_forensic: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Master Scoring Function: Evaluates all 6 pillars, computes consensus weighted average,
    and applies the Knock-Out / Veto safety check with real-time news/regulatory guardrails.
    """
    s1, exp1 = score_pillar_1_financial_health(quant, screener)
    s2, exp2 = score_pillar_2_growth_momentum(quant, screener)
    s3, exp3 = score_pillar_3_moat_and_market_share(ai_data, screener)
    s4, exp4 = score_pillar_4_governance_and_forensics(ai_data, screener, news_forensic)
    s5, exp5 = score_pillar_5_longevity_and_survival(ai_data, news_forensic)
    s6, exp6 = score_pillar_6_valuation_and_margin_of_safety(quant, screener)
    
    raw_weighted = (
        s1 * PILLAR_WEIGHTS["financial_health"] +
        s2 * PILLAR_WEIGHTS["growth_momentum"] +
        s3 * PILLAR_WEIGHTS["moat_market_share"] +
        s4 * PILLAR_WEIGHTS["management_governance"] +
        s5 * PILLAR_WEIGHTS["longevity_survival"] +
        s6 * PILLAR_WEIGHTS["valuation_margin_of_safety"]
    )
    
    # Enforce Knock-Out Veto Rule
    knockout_triggered = False
    knockout_reason = None
    final_score = round(raw_weighted, 2)
    verdict = "INVEST / STRONG COMPOUNDER" if final_score >= 7.5 else ("HOLD / MODERATE QUALITY" if final_score >= 6.0 else "AVOID / WEAK METRICS")
    
    if s4 < KNOCKOUT_THRESHOLDS["min_governance_score"]:
        knockout_triggered = True
        knockout_reason = f"VETO TRIGGERED: Pillar 4 Governance Score ({s4}/10) fell below safety threshold ({KNOCKOUT_THRESHOLDS['min_governance_score']}/10)."
        final_score = min(final_score, KNOCKOUT_THRESHOLDS["max_capped_overall_score"])
        verdict = "VETO AVOID / GOVERNANCE RED FLAG"
    elif s5 < KNOCKOUT_THRESHOLDS["min_longevity_score"]:
        knockout_triggered = True
        knockout_reason = f"VETO TRIGGERED: Pillar 5 Longevity Score ({s5}/10) fell below safety threshold ({KNOCKOUT_THRESHOLDS['min_longevity_score']}/10)."
        final_score = min(final_score, KNOCKOUT_THRESHOLDS["max_capped_overall_score"])
        verdict = "VETO AVOID / HIGH DISRUPTION OR REGULATORY RISK"
        
    scorecard = {
        "ticker": quant.get("ticker", "UNKNOWN"),
        "company_name": quant.get("company_name", "Unknown Company"),
        "sector": quant.get("sector", "Unknown"),
        "current_price": quant.get("current_price", 0.0),
        "market_cap_cr": quant.get("market_cap_cr", 0.0),
        "final_weighted_score": final_score,
        "raw_weighted_score": round(raw_weighted, 2),
        "investment_verdict": verdict,
        "knockout_triggered": knockout_triggered,
        "knockout_reason": knockout_reason,
        "pillars": {
            "1_financial_health": {"score": s1, "weight_pct": 15, "summary": exp1},
            "2_growth_momentum": {"score": s2, "weight_pct": 15, "summary": exp2},
            "3_moat_market_share": {"score": s3, "weight_pct": 24, "summary": exp3},
            "4_management_governance": {"score": s4, "weight_pct": 24, "summary": exp4},
            "5_longevity_survival": {"score": s5, "weight_pct": 8, "summary": exp5},
            "6_valuation_safety": {"score": s6, "weight_pct": 14, "summary": exp6}
        }
    }
    
    return scorecard


if __name__ == "__main__":
    print("Scoring Engine ready.")
