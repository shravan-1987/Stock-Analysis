#!/usr/bin/env python3
"""
Master Entrypoint for the Indian Stock Analysis Engine (`Stock-Analysis`)
Usage:
    python main.py --stock RELIANCE
    python main.py --stock TCS --fast
"""

import sys
import argparse
import logging
from pathlib import Path

from src.extractors.quantitative import fetch_yfinance_metrics
from src.scrapers.screener_scraper import scrape_full_screener_data
from src.scrapers.pdf_downloader import download_annual_reports_for_ticker
from src.extractors.pdf_ai_analyzer import analyze_company_annual_reports, analyze_pdf_local_fallback
from src.scrapers.news_forensic_scraper import scrape_live_news_forensics
from src.engine.scoring import compute_final_scorecard
from src.engine.report_generator import render_terminal_scorecard, export_scorecard_files

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_stock_analysis(ticker: str, fast_mode: bool = False, force_download: bool = False) -> dict:
    """
    Executes the complete end-to-end 6-Pillar analysis pipeline for an Indian stock ticker.
    """
    logger.info(f"=== INITIATING STOCK ANALYSIS PIPELINE FOR: {ticker.upper()} ===")
    
    # 1. Fetch real-time quantitative metrics from yfinance
    quant_data = fetch_yfinance_metrics(ticker)
    
    # 2. Scrape historical tables, CAGR boxes, and pledging from Screener.in
    screener_data = scrape_full_screener_data(ticker)
    
    # 3. Handle Annual Report PDFs and AI Forensic Extraction
    ai_data = {}
    if fast_mode:
        logger.info("Fast mode enabled (--fast): Skipping multi-megabyte PDF downloads and using local ratio estimates.")
        ai_data = analyze_pdf_local_fallback(Path("fast_mode_dummy.pdf"))
    else:
        logger.info("Checking & downloading last 3 years of Annual Report PDFs from Screener...")
        download_results = download_annual_reports_for_ticker(ticker, max_reports=3, force=force_download)
        valid_pdf_paths = [Path(item["file_path"]) for item in download_results if item.get("file_path") and Path(item["file_path"]).exists()]
        
        if valid_pdf_paths:
            logger.info(f"Running Gemini 3.1 Pro / AI extraction across {len(valid_pdf_paths)} downloaded Annual Reports...")
            ai_data = analyze_company_annual_reports(valid_pdf_paths)
        else:
            logger.warning("Could not download valid PDF Annual Reports. Using local fallback estimates.")
            ai_data = analyze_pdf_local_fallback(Path("no_reports_dummy.pdf"))
            
    # 3.5 Run Live News & Regulatory Forensic Scraper (ED/CBI/SEBI/NCLT pre-check)
    logger.info("Checking live news & regulatory forensic intelligence...")
    news_forensic = scrape_live_news_forensics(ticker, quant_data.get("company_name", ""))
            
    # 4. Run Consensus Scoring Engine (15-15-24-24-8-14 + Knock-Out Veto Rule)
    logger.info("Computing 6-Pillar consensus scorecard and checking Knock-Out safety rules...")
    scorecard = compute_final_scorecard(quant_data, screener_data, ai_data, news_forensic)
    
    # 5. Render to terminal and export JSON/Markdown
    render_terminal_scorecard(scorecard)
    export_scorecard_files(scorecard)
    
    logger.info(f"=== STOCK ANALYSIS PIPELINE COMPLETE FOR: {ticker.upper()} ===")
    return scorecard


def main():
    parser = argparse.ArgumentParser(description="Indian Stock Analysis & 6-Pillar AI Evaluation Engine")
    parser.add_argument("-s", "--stock", type=str, required=True, help="Stock ticker symbol or name (e.g., RELIANCE, TCS, TATAMOTORS, INFY)")
    parser.add_argument("-f", "--fast", action="store_true", help="Fast mode: Skip downloading large Annual Report PDFs and compute score immediately")
    parser.add_argument("--force-download", action="store_true", help="Force re-download of Annual Report PDFs even if cached locally")
    
    args = parser.parse_args()
    
    try:
        run_stock_analysis(args.stock, fast_mode=args.fast, force_download=args.force_download)
    except Exception as e:
        logger.error(f"Fatal error during stock analysis execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
