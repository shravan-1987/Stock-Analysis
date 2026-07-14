"""
Annual Report PDF Downloader Module
Responsible for downloading, validating, and locally caching multi-year Annual Report
PDF files from Screener / BSE / NSE links into `data/annual_reports/{ticker}/`.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from pypdf import PdfReader

from src.utils.config import ANNUAL_REPORTS_DIR, DEFAULT_USER_AGENT, REQUEST_TIMEOUT_SECONDS
from src.scrapers.screener_scraper import get_clean_ticker, scrape_full_screener_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ticker_report_dir(ticker: str) -> Path:
    """Returns and creates the dedicated cache folder for a ticker's annual reports."""
    clean = get_clean_ticker(ticker)
    ticker_dir = ANNUAL_REPORTS_DIR / clean
    ticker_dir.mkdir(parents=True, exist_ok=True)
    return ticker_dir


def is_valid_pdf(file_path: Path) -> bool:
    """Checks if a downloaded file exists, has non-zero size, and is a valid PDF."""
    if not file_path.exists() or file_path.stat().st_size < 10240:  # < 10KB is likely HTML error
        return False
    try:
        reader = PdfReader(str(file_path))
        if len(reader.pages) > 0:
            return True
    except Exception:
        return False
    return False


def download_single_report(url: str, ticker: str, year_label: str, force: bool = False) -> Optional[Path]:
    """
    Downloads a single Annual Report PDF for a given ticker and financial year.
    If cached and valid, skips download unless `force=True`.
    """
    clean_ticker = get_clean_ticker(ticker)
    ticker_dir = get_ticker_report_dir(clean_ticker)
    
    # Sanitize year_label (e.g. "FY 2024" -> "FY_2024.pdf")
    safe_year = year_label.replace(" ", "_").replace("/", "_").strip()
    if not safe_year.endswith(".pdf"):
        safe_year = f"{safe_year}.pdf"
        
    destination = ticker_dir / safe_year
    
    # Check cache
    if not force and is_valid_pdf(destination):
        logger.info(f"Using cached valid PDF for {clean_ticker} ({year_label}): {destination}")
        return destination
        
    logger.info(f"Downloading Annual Report PDF for {clean_ticker} ({year_label}) from {url}...")
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/pdf,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8"
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=REQUEST_TIMEOUT_SECONDS * 2)
        if response.status_code == 200:
            with open(destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            if is_valid_pdf(destination):
                logger.info(f"Successfully downloaded and validated: {destination}")
                return destination
            else:
                logger.warning(f"Downloaded file for {year_label} is not a valid PDF or corrupted: {destination}")
                if destination.exists():
                    destination.unlink(missing_ok=True)
        else:
            logger.warning(f"Failed to download {url} - Status Code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        if destination.exists():
            destination.unlink(missing_ok=True)
            
    return None


def download_annual_reports_for_ticker(ticker: str, max_reports: int = 3, force: bool = False) -> List[Dict[str, Any]]:
    """
    Master function: Scrapes Screener.in for download links and fetches up to `max_reports`
    Annual Report PDFs for the ticker. Returns list of metadata with local `file_path`.
    """
    clean_ticker = get_clean_ticker(ticker)
    logger.info(f"Starting Annual Reports download pipeline for: {clean_ticker}")
    
    screener_data = scrape_full_screener_data(clean_ticker)
    links = screener_data.get("annual_report_links", [])
    
    results = []
    for item in links[:max_reports]:
        year_label = item.get("year", "Unknown_Year")
        url = item.get("url")
        if not url:
            continue
            
        file_path = download_single_report(url, clean_ticker, year_label, force=force)
        results.append({
            "year": year_label,
            "url": url,
            "file_path": str(file_path) if file_path else None,
            "status": "SUCCESS" if file_path else "FAILED"
        })
        
    return results


if __name__ == "__main__":
    # Test execution on RELIANCE (fetching top 1 report for speed)
    res = download_annual_reports_for_ticker("RELIANCE", max_reports=1)
    print("\n--- DOWNLOAD PIPELINE RESULT ---")
    for r in res:
        print(f"Year: {r['year']} | Status: {r['status']} | Path: {r['file_path']}")
