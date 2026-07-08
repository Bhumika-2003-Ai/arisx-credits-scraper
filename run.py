"""
ArisX Startup Credits Scraper
Entry point with CLI flags + scheduler.
"""

import argparse
import schedule
import time
from rich.console import Console
from dotenv import load_dotenv

# ✅ IMPORTS
from alerts.emailer import send_email
from db.database import init_db, save_to_db

load_dotenv()
console = Console()


# ✅ NEW: DATA CLEANING FUNCTION
def is_valid_program(p):
    if not p.program_name:
        return False

    name = p.program_name.lower()

    junk_keywords = [
        "review", "★★★★★", "every", "yes —",
        "most credits", "startup credits are free",
        "top credits"
    ]

    if any(j in name for j in junk_keywords):
        return False

    if len(name.strip()) < 12:
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="ArisX Startup Credits Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py
  python run.py --dry-run
  python run.py --schedule
  python run.py --schedule --interval 6
        """
    )

    parser.add_argument("--dry-run", action="store_true", help="Run without pushing to Sheets")
    parser.add_argument("--json", action="store_true", help="Output results as JSON (implies --dry-run)")
    parser.add_argument("--schedule", action="store_true", help="Run on a recurring schedule")
    parser.add_argument("--interval", type=int, default=24, help="Schedule interval in hours")

    args = parser.parse_args()

    if args.json:
        args.dry_run = True

    from pipeline import run_pipeline

    # ─────────────────────────────────────────
    # 🚀 JOB FUNCTION
    # ─────────────────────────────────────────
    def job():
        try:
            console.rule("[bold cyan]🚀 Starting Pipeline[/bold cyan]")

            result = run_pipeline(
                dry_run=args.dry_run,
                json_output=args.json,
                return_data=True
            )

            if not result:
                console.print("[red]Pipeline returned no data[/red]")
                return

            programs, news_items = result

            # ✅ CLEAN DATA
            programs = [p for p in programs if is_valid_program(p)]

            console.print(f"[cyan]Programs after cleaning:[/cyan] {len(programs)}")
            console.print(f"[cyan]News scraped:[/cyan] {len(news_items)}")

            # ✅ DATABASE
            init_db()
            save_to_db(programs)

            # ✅ EMAIL (SAFE)
            new_programs = programs[:5]
            try:
                send_email(new_programs)
            except Exception as e:
                console.print(f"[yellow]Email skipped: {e}[/yellow]")

            # ✅ DRY RUN
            if args.dry_run:
                console.print("[yellow]Dry run complete — nothing pushed[/yellow]\n")
                return

            # ✅ GOOGLE SHEETS
            from sheets.sheets_manager import push_programs, push_news, log_run

            console.print("[cyan]Pushing data to Google Sheets...[/cyan]")

            new_count, updated_count = push_programs(programs)
            news_count = push_news(news_items)

            log_run(
                total_programs=len(programs),
                new_count=new_count,
                updated_count=updated_count,
                news_count=news_count
            )

            console.print(
                f"[bold green]✓ Done: {new_count} new, {updated_count} updated, {news_count} news[/bold green]\n"
            )

        except Exception as e:
            console.print(f"[bold red]Pipeline error: {e}[/bold red]")
            import traceback
            traceback.print_exc()

    # ─────────────────────────────────────────
    # ⏱️ SCHEDULER
    # ─────────────────────────────────────────
    if args.schedule:
        console.print(f"[bold cyan]Scheduler started — every {args.interval} hours[/bold cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        job()
        schedule.every(args.interval).hours.do(job)

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            console.print("\n[yellow]Scheduler stopped[/yellow]")

    else:
        job()


if __name__ == "__main__":
    main()