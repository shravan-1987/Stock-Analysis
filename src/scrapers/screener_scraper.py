"""
Screener.in HTML Scraper Module
Responsible for scraping Screener.in for 10-year quantitative financial tables,
compounded CAGR tables, shareholding pattern (Promoter Pledging %), and exact
download URLs for the last 3 years of Annual Reports.
"""

import re
import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup

from src.utils.config import DEFAULT_USER_AGENT, REQUEST_TIMEOUT_SECONDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_clean_ticker(raw_ticker: str) -> str:
    """Removes .NS or .BO suffixes for Screener.in URLs (e.g., RELIANCE.NS -> RELIANCE)."""
    clean = raw_ticker.strip().upper()
    for suffix in [".NS", ".BO", ".BSE", ".NSE"]:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)]
    return clean


def fetch_screener_page(ticker: str, consolidated: bool = True) -> Optional[BeautifulSoup]:
    """
    Fetches the Screener.in HTML page for a given ticker using BeautifulSoup.
    Tries the /consolidated/ URL first; if 404, falls back to standalone URL.
    """
    clean_ticker = get_clean_ticker(ticker)
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    
    urls_to_try = [
        f"https://www.screener.in/company/{clean_ticker}/consolidated/",
        f"https://www.screener.in/company/{clean_ticker}/"
    ] if consolidated else [f"https://www.screener.in/company/{clean_ticker}/"]
    
    for url in urls_to_try:
        try:
            logger.info(f"Fetching Screener URL: {url}")
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Verify it is a valid company page and not a search redirect
                if soup.find("h1"):
                    return soup
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            
    logger.error(f"Could not load Screener page for {clean_ticker}")
    return None


def extract_annual_report_links(soup: BeautifulSoup, last_n_years: int = 3) -> List[Dict[str, str]]:
    """
    Scrapes the #documents section (`Annual reports`) on Screener.in and returns
    a list of dictionaries containing exact PDF download URLs and financial years.
    Example output: [{'year': 'FY 2025', 'url': 'https://...'}, ...]
    """
    reports: List[Dict[str, str]] = []
    if not soup:
        return reports
        
    doc_section = soup.find("section", id="documents")
    if not doc_section:
        return reports
        
    # Find the subsection titled "Annual reports"
    for heading in doc_section.find_all(["h2", "h3", "h4", "div"]):
        if "annual report" in heading.text.lower():
            # The links are typically inside the next ul or div sibling/container
            parent_container = heading.find_parent("div") or doc_section
            links = parent_container.find_all("a", href=True)
            for link in links:
                text = link.text.strip()
                href = link["href"].strip()
                # Match FY years like "FY 2024", "Financial Year 2023", or just "2024"
                year_match = re.search(r"(?:FY\s*|Financial Year\s*)?(\d{4})", text, re.IGNORECASE)
                if year_match and ("pdf" in href.lower() or "bseindia.com" in href.lower() or "nseindia.com" in href.lower() or "screener.in" in href.lower()):
                    year_num = int(year_match.group(1))
                    # Only include reasonable recent financial years (e.g., >= 2020)
                    if year_num >= 2020:
                        reports.append({
                            "year": f"FY {year_num}",
                            "year_num": year_num,
                            "url": href if href.startswith("http") else f"https://www.screener.in{href}"
                        })
            break
            
    # Remove duplicates and sort descending by year
    seen_years = set()
    unique_reports = []
    # Sort descending by year_num
    reports.sort(key=lambda x: x.get("year_num", 0), reverse=True)
    for rep in reports:
        if rep["year_num"] not in seen_years:
            seen_years.add(rep["year_num"])
            unique_reports.append(rep)
            if len(unique_reports) >= last_n_years:
                break
                
    return unique_reports


def extract_compounded_growth_tables(soup: BeautifulSoup) -> Dict[str, Dict[str, float]]:
    """
    Extracts the summary CAGR boxes on Screener.in:
    - Compounded Sales Growth (10Y, 5Y, 3Y, TTM)
    - Compounded Profit Growth (10Y, 5Y, 3Y, TTM)
    - Stock Price CAGR (10Y, 5Y, 3Y, 1Y)
    - Return on Equity (10Y, 5Y, 3Y, Last Year)
    """
    cagr_tables = {
        "sales_growth": {},
        "profit_growth": {},
        "stock_price_cagr": {},
        "return_on_equity": {}
    }
    if not soup:
        return cagr_tables
        
    # These tables usually sit under #profit-loss in small tables with class 'ranges-table'
    tables = soup.find_all("table", class_="ranges-table")
    for table in tables:
        header = table.find("th")
        if not header:
            continue
        header_text = header.text.lower()
        
        target_key = None
        if "sales growth" in header_text:
            target_key = "sales_growth"
        elif "profit growth" in header_text:
            target_key = "profit_growth"
        elif "stock price" in header_text:
            target_key = "stock_price_cagr"
        elif "return on equity" in header_text:
            target_key = "return_on_equity"
            
        if target_key:
            rows = table.find_all("tr")[1:]  # skip header
            for tr in rows:
                cols = tr.find_all("td")
                if len(cols) == 2:
                    period = cols[0].text.strip()
                    val_str = cols[1].text.strip().replace("%", "").replace(",", "")
                    try:
                        cagr_tables[target_key][period] = float(val_str)
                    except ValueError:
                        pass
                        
    return cagr_tables


def extract_ratios_and_efficiency(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extracts Return on Capital Employed (ROCE %), Working Capital Days, and Debtor Days
    from the #ratios table.
    """
    ratios = {
        "roce_pct_latest": 0.0,
        "roce_trend": {},
        "debtor_days_latest": 0.0,
        "working_capital_days_latest": 0.0
    }
    if not soup:
        return ratios
        
    ratios_section = soup.find("section", id="ratios")
    if not ratios_section:
        return ratios
        
    table = ratios_section.find("table")
    if not table:
        return ratios
        
    # Extract headers (Years)
    headers = [th.text.strip() for th in table.find_all("th")]
    
    for tr in table.find_all("tr"):
        tds = [td.text.strip() for td in tr.find_all("td")]
        if not tds:
            continue
        row_name = tds[0].lower()
        
        if "roce" in row_name:
            for i, val in enumerate(tds[1:], start=1):
                clean_val = val.replace("%", "").replace(",", "").strip()
                try:
                    num = float(clean_val)
                    year_label = headers[i] if i < len(headers) else f"Yr_{i}"
                    ratios["roce_trend"][year_label] = num
                    ratios["roce_pct_latest"] = num  # last valid is latest
                except ValueError:
                    pass
        elif "debtor days" in row_name:
            for val in reversed(tds[1:]):
                try:
                    ratios["debtor_days_latest"] = float(val.replace(",", "").strip())
                    break
                except ValueError:
                    continue
        elif "working capital days" in row_name:
            for val in reversed(tds[1:]):
                try:
                    ratios["working_capital_days_latest"] = float(val.replace(",", "").strip())
                    break
                except ValueError:
                    continue
                    
    return ratios


def extract_shareholding_pattern(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extracts Promoter Holding %, FII/DII %, and specifically detects Promoter Pledging %
    from the #shareholding section on Screener.in.
    """
    shareholding = {
        "promoter_holding_pct": 0.0,
        "fii_holding_pct": 0.0,
        "dii_holding_pct": 0.0,
        "public_holding_pct": 0.0,
        "promoter_pledging_pct": 0.0,
        "pledging_detected": False
    }
    if not soup:
        return shareholding
        
    sh_section = soup.find("section", id="shareholding")
    if not sh_section:
        return shareholding
        
    # Look for table rows
    for tr in sh_section.find_all("tr"):
        tds = [td.text.strip() for td in tr.find_all(["td", "th"])]
        if not tds or len(tds) < 2:
            continue
        row_name = tds[0].lower()
        
        # Get latest number (last column usually)
        latest_num = 0.0
        for val in reversed(tds[1:]):
            try:
                latest_num = float(val.replace("%", "").replace(",", "").strip())
                break
            except ValueError:
                continue
                
        if "promoters" in row_name:
            shareholding["promoter_holding_pct"] = latest_num
        elif "fii" in row_name:
            shareholding["fii_holding_pct"] = latest_num
        elif "dii" in row_name:
            shareholding["dii_holding_pct"] = latest_num
        elif "public" in row_name:
            shareholding["public_holding_pct"] = latest_num
        elif "pledged" in row_name:
            shareholding["promoter_pledging_pct"] = latest_num
            shareholding["pledging_detected"] = latest_num > 0.0
            
    return shareholding


def scrape_full_screener_data(ticker: str) -> Dict[str, Any]:
    """
    Master function: Scrapes Screener.in for a given ticker and returns a comprehensive
    dictionary containing Annual Report PDF links, CAGR growth boxes, efficiency ratios,
    and shareholding/pledging metrics.
    """
    soup = fetch_screener_page(ticker, consolidated=True)
    if not soup:
        return {"ticker": ticker, "error": "Could not fetch Screener HTML"}
        
    annual_reports = extract_annual_report_links(soup, last_n_years=3)
    cagr_tables = extract_compounded_growth_tables(soup)
    ratios = extract_ratios_and_efficiency(soup)
    shareholding = extract_shareholding_pattern(soup)
    
    return {
        "ticker": get_clean_ticker(ticker),
        "annual_report_links": annual_reports,
        "cagr_growth": cagr_tables,
        "efficiency_ratios": ratios,
        "shareholding_pattern": shareholding
    }


if __name__ == "__main__":
    # Test execution on RELIANCE
    result = scrape_full_screener_data("RELIANCE")
    print("\n--- SCREENER SCRAPE RESULT FOR RELIANCE ---")
    print(f"Annual Report Links: {result.get('annual_report_links')}")
    print(f"Latest ROCE: {result.get('efficiency_ratios', {}).get('roce_pct_latest')}%")
    print(f"Promoter Pledging: {result.get('shareholding_pattern', {}).get('promoter_pledging_pct')}%")
