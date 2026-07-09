"""
Core pipeline: runs all scrapers, deduplicates, returns data to runner.
FINAL STABLE VERSION
"""

import dataclasses
import json
from rich.console import Console
from rich.table import Table

from scrapers.world_bank_scraper import fetch_programs as scrape_world_bank
from scrapers.scraper_seed import scrape as scrape_seed
from scrapers.scraper_creditforstartups import scrape as scrape_creditforstartups
from scrapers.scraper_trueup import scrape as scrape_trueup
from scrapers.scraper_klymentiev import scrape as scrape_klymentiev
from scrapers.scraper_startupcredits import scrape as scrape_startupcredits

from scrapers.news_fetcher import fetch_all_news

# ✅ FIXED IMPORT
from utils.models import CreditProgram

console = Console()


# ─────────────────────────────────────────────
# DEDUP
# ─────────────────────────────────────────────
def _deduplicate(programs: list[CreditProgram]) -> list[CreditProgram]:
    seen: dict[str, CreditProgram] = {}

    for p in programs:
        try:
            seen[p.dedup_key] = p
        except Exception:
            continue

    return list(seen.values())


# ─────────────────────────────────────────────
# SAFE SCRAPER RUNNER
# ─────────────────────────────────────────────
def _run_scraper(name, scrape_fn):
    try:
        results = scrape_fn()
        console.print(f"[green]✓ {name}: {len(results)} items[/green]")
        return results
    except Exception as e:
        console.print(f"[red]✗ {name} failed: {e}[/red]")
        return []


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def run_pipeline(
    dry_run: bool = False,
    json_output: bool = False,
    return_data: bool = False
):
    import sys

    if json_output:
        sys.stdout = sys.stderr

    console.rule("[bold cyan]⚡ ArisX Credits Scraper — Starting Pipeline[/bold cyan]")

    # ─────────────────────────────────────────
    # 1. RUN SCRAPERS
    # ─────────────────────────────────────────
    all_programs: list[CreditProgram] = []

    all_programs += _run_scraper("seed", scrape_seed)
    all_programs += _run_scraper("world_bank", scrape_world_bank)  # ✅ added properly

    scrapers = [
        ("creditforstartups.com", scrape_creditforstartups),
        ("trueup.io", scrape_trueup),
        ("klymentiev.com", scrape_klymentiev),
        ("startupcredits.dev", scrape_startupcredits),
    ]

    for name, scrape_fn in scrapers:
        results = _run_scraper(name, scrape_fn)

        for item in results:
            try:
                if isinstance(item, dict):
                    program_obj = CreditProgram(
                        provider=item.get("provider", "Unknown"),
                        program_name=item.get("program_name", "Unknown"),
                        category=item.get("category", "Startup Credits"),
                        credit_amount=item.get("credit_amount", "Unknown"),
                        validity=item.get("validity", "Unknown"),
                        eligibility=item.get("eligibility", "Unknown"),
                        requires_vc=item.get("requires_vc", "Unknown"),
                        apply_url=item.get("apply_url", ""),
                        notes=item.get("notes", ""),
                        source_site=item.get("source_site", name),
                    )
                    all_programs.append(program_obj)
                else:
                    all_programs.append(item)
            except Exception:
                continue

    # ─────────────────────────────────────────
    # 2. DEDUP
    # ─────────────────────────────────────────
    unique_programs = _deduplicate(all_programs)

    console.print(
        f"\n[bold green]Total unique programs: {len(unique_programs)}[/bold green]"
    )

    # ─────────────────────────────────────────
    # 3. TABLE VIEW
    # ─────────────────────────────────────────
    table = Table(title="Programs Found", show_lines=True)
    table.add_column("Provider", style="cyan", width=18)
    table.add_column("Program", width=28)
    table.add_column("Category", width=20)
    table.add_column("Credits", style="green", width=18)
    table.add_column("VC?", width=6)

    for p in sorted(unique_programs, key=lambda x: x.category):
        table.add_row(
            p.provider,
            p.program_name[:28],
            p.category,
            p.credit_amount[:18],
            p.requires_vc,
        )

    console.print(table)

    # ─────────────────────────────────────────
    # 4. FETCH NEWS
    # ─────────────────────────────────────────
    console.print("\n[bold cyan]📰 Fetching news...[/bold cyan]")

    try:
        news_items = fetch_all_news()
        console.print(f"[green]✓ News fetched: {len(news_items)}[/green]")
    except Exception as e:
        console.print(f"[red]News fetch failed: {e}[/red]")
        news_items = []

    # ─────────────────────────────────────────
    # 5. OUTPUT MODES
    # ─────────────────────────────────────────
    if json_output:
        output = {
            "programs": [dataclasses.asdict(p) for p in unique_programs],
            "news": news_items,
            "total_programs": len(unique_programs),
            "total_news": len(news_items),
        }
        sys.__stdout__.write(json.dumps(output, indent=2, ensure_ascii=False) + "\n")

    elif dry_run:
        console.print("\n[yellow]DRY RUN — skipping Google Sheets[/yellow]")
        console.print(f"Programs: {len(unique_programs)}")
        console.print(f"News: {len(news_items)}")

    if return_data:
        return unique_programs, news_items

    console.rule("[bold green]✓ Pipeline Complete[/bold green]")

    return {
        "total_programs": len(unique_programs),
        "news_items": len(news_items),
    }
