"""
Quantitative Extractor Module (`yfinance`)
Responsible for fetching real-time market data, valuation multiples, and historical CAGR
metrics for Indian equities (.NS / .BO).
"""

import logging
from typing import Dict, Any, Optional
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_indian_ticker(raw_ticker: str) -> str:
    """
    Normalizes an Indian stock ticker to format expected by yfinance (.NS for NSE, .BO for BSE).
    If no suffix is provided, defaults to .NS (National Stock Exchange).
    """
    clean = raw_ticker.strip().upper()
    if clean.endswith(".NS") or clean.endswith(".BO"):
        return clean
    return f"{clean}.NS"


def fetch_yfinance_metrics(ticker_symbol: str) -> Dict[str, Any]:
    """
    Fetches real-time quantitative metrics and valuation ratios for a given ticker.
    Automatically attempts fallback to .BO (BSE) if .NS yields no data.
    """
    normalized = normalize_indian_ticker(ticker_symbol)
    logger.info(f"Fetching quantitative metrics from yfinance for: {normalized}")
    
    stock = yf.Ticker(normalized)
    info = stock.info
    
    # Check if data exists; if not, fallback to .BO if it was .NS
    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        if normalized.endswith(".NS"):
            bse_ticker = normalized.replace(".NS", ".BO")
            logger.warning(f"No data for {normalized}. Falling back to BSE: {bse_ticker}")
            stock = yf.Ticker(bse_ticker)
            info = stock.info
            normalized = bse_ticker
            
    # Extract robust price & valuation fields
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    if current_price is None:
        # Fallback to 1-day history
        hist = stock.history(period="1d")
        if not hist.empty:
            current_price = float(hist["Close"].iloc[-1])
        else:
            current_price = 0.0

    market_cap = info.get("marketCap", 0)
    pe_ratio = info.get("trailingPE") or info.get("forwardPE", 0.0)
    pb_ratio = info.get("priceToBook", 0.0)
    ev_ebitda = info.get("enterpriseToEbitda", 0.0)
    dividend_yield = (info.get("dividendYield", 0.0) or 0.0) * 100  # Convert to percentage
    high_52w = info.get("fiftyTwoWeekHigh", 0.0)
    low_52w = info.get("fiftyTwoWeekLow", 0.0)
    sector = info.get("sector", "Unknown Sector")
    industry = info.get("industry", "Unknown Industry")
    company_name = info.get("longName") or info.get("shortName") or normalized

    # Extract historical revenue & profit CAGR if financials exist
    cagr_data = calculate_historical_cagr(stock)

    metrics = {
        "ticker": normalized,
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
        "current_price": round(float(current_price), 2),
        "market_cap_cr": round(float(market_cap) / 10000000.0, 2) if market_cap else 0.0,  # Convert INR to Crores
        "pe_ratio": round(float(pe_ratio), 2) if pe_ratio else 0.0,
        "pb_ratio": round(float(pb_ratio), 2) if pb_ratio else 0.0,
        "ev_ebitda": round(float(ev_ebitda), 2) if ev_ebitda else 0.0,
        "dividend_yield_pct": round(float(dividend_yield), 2),
        "fifty_two_week_high": round(float(high_52w), 2) if high_52w else 0.0,
        "fifty_two_week_low": round(float(low_52w), 2) if low_52w else 0.0,
        "yfinance_cagr": cagr_data
    }
    
    return metrics


def calculate_historical_cagr(stock: yf.Ticker) -> Dict[str, float]:
    """
    Computes 3-year or available historical CAGR for Revenue and Net Income
    from yfinance financial statement tables.
    """
    cagr_results = {
        "revenue_cagr_pct": 0.0,
        "net_profit_cagr_pct": 0.0
    }
    try:
        financials = stock.financials
        if financials is None or financials.empty:
            return cagr_results
            
        # Get revenue row
        rev_rows = [row for row in financials.index if "Total Revenue" in str(row) or "Operating Revenue" in str(row)]
        if rev_rows:
            rev_series = financials.loc[rev_rows[0]].dropna()
            if len(rev_series) >= 2:
                latest_rev = float(rev_series.iloc[0])
                oldest_rev = float(rev_series.iloc[-1])
                years = len(rev_series) - 1
                if oldest_rev > 0 and years > 0:
                    cagr_results["revenue_cagr_pct"] = round(((latest_rev / oldest_rev) ** (1 / years) - 1) * 100, 2)
                    
        # Get net income row
        pat_rows = [row for row in financials.index if "Net Income" in str(row) or "Net Profit" in str(row)]
        if pat_rows:
            pat_series = financials.loc[pat_rows[0]].dropna()
            if len(pat_series) >= 2:
                latest_pat = float(pat_series.iloc[0])
                oldest_pat = float(pat_series.iloc[-1])
                years = len(pat_series) - 1
                if oldest_pat > 0 and years > 0:
                    cagr_results["net_profit_cagr_pct"] = round(((latest_pat / oldest_pat) ** (1 / years) - 1) * 100, 2)
    except Exception as e:
        logger.warning(f"Could not calculate yfinance CAGR: {e}")
        
    return cagr_results


if __name__ == "__main__":
    # Test execution on RELIANCE
    res = fetch_yfinance_metrics("RELIANCE")
    print(res)
