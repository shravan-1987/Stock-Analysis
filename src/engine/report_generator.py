"""
Report Generator Module
Formats and renders the executive 10-Point Scorecard inside the terminal using Rich / ASCII Box,
and exports the structured results to JSON and Markdown files inside `data/cache/`.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

from src.utils.config import CACHE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def render_terminal_scorecard(scorecard: Dict[str, Any]) -> None:
    """Renders an executive scorecard directly inside the terminal."""
    ticker = scorecard.get("ticker", "UNKNOWN")
    company = scorecard.get("company_name", "Unknown")
    price = scorecard.get("current_price", 0.0)
    mcap = scorecard.get("market_cap_cr", 0.0)
    final_score = scorecard.get("final_weighted_score", 0.0)
    verdict = scorecard.get("investment_verdict", "UNKNOWN")
    knockout = scorecard.get("knockout_triggered", False)
    knockout_reason = scorecard.get("knockout_reason")
    
    if HAS_RICH:
        console = Console()
        
        # Header Panel
        header_text = f"[bold cyan]{company} ({ticker})[/bold cyan]\n"
        header_text += f"Current Price: [green]Rs. {price:,.2f}[/green] | Market Cap: [yellow]Rs. {mcap:,.2f} Cr[/yellow]"
        console.print(Panel(header_text, title="[bold white]INDIAN STOCK EVALUATION SCORECARD[/bold white]", border_style="cyan"))
        
        # Pillars Table
        table = Table(box=box.ROUNDED, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Evaluation Pillar", style="bold white", width=36)
        table.add_column("Weight", justify="right", style="cyan", width=8)
        table.add_column("Score (0-10)", justify="right", style="bold green", width=12)
        table.add_column("Key Analysis & Drivers", style="italic white")
        
        pillars = scorecard.get("pillars", {})
        for idx_key, p_data in sorted(pillars.items()):
            p_num = idx_key.split("_")[0]
            p_name = idx_key.split("_", 1)[1].replace("_", " ").title()
            score_val = p_data.get("score", 0.0)
            weight_val = p_data.get("weight_pct", 0)
            summary_val = p_data.get("summary", "")
            
            # Color score
            score_str = f"[bold green]{score_val:.1f} / 10[/bold green]" if score_val >= 7.5 else (
                f"[bold yellow]{score_val:.1f} / 10[/bold yellow]" if score_val >= 5.5 else f"[bold red]{score_val:.1f} / 10[/bold red]"
            )
            table.add_row(p_num, p_name, f"{weight_val}%", score_str, summary_val)
            
        console.print(table)
        
        # Final Verdict Box
        verdict_color = "red" if knockout or final_score < 5.5 else ("yellow" if final_score < 7.5 else "green")
        verdict_text = f"[bold white]OVERALL CONSENSUS HEALTH SCORE:[/bold white] [{verdict_color}]{final_score:.2f} / 10.0[/{verdict_color}]\n"
        verdict_text += f"[bold white]INVESTMENT VERDICT:[/bold white] [{verdict_color}]{verdict}[/{verdict_color}]"
        
        if knockout and knockout_reason:
            verdict_text += f"\n\n[bold red][ALERT] {knockout_reason}[/bold red]"
            
        console.print(Panel(verdict_text, title="[bold white]EXECUTIVE VERDICT[/bold white]", border_style=verdict_color))
    else:
        # Fallback ASCII print
        print("\n" + "="*80)
        print(f"STOCK ANALYSIS SCORECARD: {company} ({ticker})")
        print(f"Price: Rs. {price:,.2f} | Market Cap: Rs. {mcap:,.2f} Cr")
        print("="*80)
        for idx_key, p_data in sorted(scorecard.get("pillars", {}).items()):
            print(f"[{p_data.get('weight_pct')}%] {idx_key.replace('_', ' ').title()}: {p_data.get('score')} / 10 -> {p_data.get('summary')}")
        print("-"*80)
        print(f"FINAL WEIGHTED SCORE: {final_score:.2f} / 10.0 ({verdict})")
        if knockout and knockout_reason:
            print(f"KNOCK-OUT VETO: {knockout_reason}")
        print("="*80 + "\n")


def export_scorecard_files(scorecard: Dict[str, Any]) -> Tuple[Path, Path]:
    """Exports JSON scorecard and Markdown report to `data/cache/` folder."""
    ticker = scorecard.get("ticker", "UNKNOWN").replace(".NS", "").replace(".BO", "")
    json_path = CACHE_DIR / f"{ticker}_scorecard.json"
    md_path = CACHE_DIR / f"{ticker}_executive_report.md"
    
    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2, ensure_ascii=False)
        
    # Save Markdown
    md_content = f"# Stock Analysis Executive Report Card: {scorecard.get('company_name')} ({scorecard.get('ticker')})\n\n"
    md_content += f"- **Current Price**: ₹{scorecard.get('current_price'):,.2f}\n"
    md_content += f"- **Market Capitalization**: ₹{scorecard.get('market_cap_cr'):,.2f} Crores\n"
    md_content += f"- **Consensus Weighted Score**: **{scorecard.get('final_weighted_score'):.2f} / 10.0**\n"
    md_content += f"- **Investment Verdict**: `{scorecard.get('investment_verdict')}`\n\n"
    
    if scorecard.get("knockout_triggered"):
        md_content += f"> [!CAUTION]\n> **Knock-Out Veto Triggered**: {scorecard.get('knockout_reason')}\n\n"
        
    md_content += "## The 6 Pillars Breakdown\n\n"
    md_content += "| # | Evaluation Pillar | Weight (%) | Score (0-10) | Key Analysis & Drivers |\n"
    md_content += "|---|---|:---:|:---:|---|\n"
    
    for idx_key, p_data in sorted(scorecard.get("pillars", {}).items()):
        p_num = idx_key.split("_")[0]
        p_name = idx_key.split("_", 1)[1].replace("_", " ").title()
        md_content += f"| **{p_num}** | {p_name} | {p_data.get('weight_pct')}% | **{p_data.get('score')}** | {p_data.get('summary')} |\n"
        
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    logger.info(f"Exported scorecard reports to: {json_path} and {md_path}")
    return json_path, md_path


if __name__ == "__main__":
    print("Report Generator module ready.")
