"""
Google Sheets manager.
Handles: auth, header setup, dedup upsert, news tab push, logging.
Optimized: batch updates to avoid quota errors.
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from utils.models import CreditProgram, SHEET_HEADERS, NEWS_HEADERS
from rich.console import Console
from datetime import datetime

console = Console()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

MAIN_TAB = "Credits Tracker"
NEWS_TAB = "News"
LOG_TAB  = "Run Log"


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────
def _get_client() -> gspread.Client:
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials.json")

    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials file not found: {creds_path}")

    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


# ─────────────────────────────────────────────────────────────
# SHEET HELPERS
# ─────────────────────────────────────────────────────────────
def _get_or_create_sheet(spreadsheet: gspread.Spreadsheet, title: str) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        console.print(f"[yellow]Creating missing sheet: {title}[/yellow]")
        return spreadsheet.add_worksheet(title=title, rows=1000, cols=20)


def _ensure_headers(ws: gspread.Worksheet, headers: list[str]):
    existing = ws.row_values(1)

    # ✅ Only set headers if empty
    if not existing:
        ws.update("A1", [headers])


def _build_dedup_map(ws: gspread.Worksheet) -> dict[str, int]:
    all_values = ws.get_all_values()
    dedup_map = {}

    for i, row in enumerate(all_values[1:], start=2):
        if len(row) >= 2:
            key = f"{row[0].lower().strip()}::{row[1].lower().strip()}"
            dedup_map[key] = i

    return dedup_map


# ─────────────────────────────────────────────────────────────
# PROGRAMS PUSH
# ─────────────────────────────────────────────────────────────
def push_programs(programs: list[CreditProgram]) -> tuple[int, int]:
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not sheet_id:
        console.print("[bold red]GOOGLE_SHEET_ID not set[/bold red]")
        return 0, 0

    console.print("[cyan]Connecting to Google Sheets...[/cyan]")

    client = _get_client()
    spreadsheet = client.open_by_key(sheet_id)
    ws = _get_or_create_sheet(spreadsheet, MAIN_TAB)

    _ensure_headers(ws, SHEET_HEADERS)

    existing_map = _build_dedup_map(ws)

    new_rows = []
    updates = []
    updated_count = 0

    for program in programs:
        key = program.dedup_key
        row_data = program.to_row()

        if key in existing_map:
            row_num = existing_map[key]
            updates.append({
                "range": f"A{row_num}",
                "values": [row_data]
            })
            updated_count += 1
        else:
            new_rows.append(row_data)

    if updates:
        ws.batch_update(updates)

    if new_rows:
        ws.append_rows(new_rows, value_input_option="RAW")

    console.print(
        f"[bold green]✓ Sheets: {len(new_rows)} new, {updated_count} updated[/bold green]"
    )

    return len(new_rows), updated_count


# ─────────────────────────────────────────────────────────────
# NEWS PUSH (🔥 FIXED)
# ─────────────────────────────────────────────────────────────
def push_news(news_items: list[dict]) -> int:
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not sheet_id:
        console.print("[red]GOOGLE_SHEET_ID missing[/red]")
        return 0

    if not news_items:
        console.print("[yellow]No news to push[/yellow]")
        return 0

    client = _get_client()
    spreadsheet = client.open_by_key(sheet_id)
    ws = _get_or_create_sheet(spreadsheet, NEWS_TAB)

    # ✅ Ensure correct headers (force fix if wrong)
    if ws.row_values(1) != NEWS_HEADERS:
        console.print("[yellow]Fixing NEWS headers...[/yellow]")
        ws.clear()
        ws.append_row(NEWS_HEADERS)

    headers = ws.row_values(1)

    # ✅ Find correct URL column dynamically
    try:
        url_index = headers.index("URL")
    except ValueError:
        console.print("[red]URL column missing[/red]")
        return 0

    existing_urls = set()
    rows = ws.get_all_values()

    for row in rows[1:]:
        if len(row) > url_index:
            existing_urls.add(row[url_index])

    new_rows = []

    for item in news_items:
        url = item.get("url", "").strip()

        if not url or url in existing_urls:
            continue

        new_rows.append([
            item.get("title", ""),
            item.get("source", ""),
            url,                        # ✅ correct position
            item.get("date", ""),       # ✅ after URL
            item.get("summary", ""),
        ])

        existing_urls.add(url)

    if new_rows:
        ws.append_rows(new_rows, value_input_option="RAW")
        console.print(f"[green]✓ News: {len(new_rows)} added[/green]")
    else:
        console.print("[yellow]No new unique news items[/yellow]")

    return len(new_rows)


# ─────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────
def log_run(total_programs: int, new_count: int, updated_count: int, news_count: int):
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not sheet_id:
        console.print("[red]GOOGLE_SHEET_ID missing[/red]")
        return

    try:
        console.print("[cyan]Writing run log...[/cyan]")

        client = _get_client()
        spreadsheet = client.open_by_key(sheet_id)
        ws = _get_or_create_sheet(spreadsheet, LOG_TAB)

        headers = [
            "Timestamp",
            "Total Programs",
            "New Rows",
            "Updated Rows",
            "News Items"
        ]

        _ensure_headers(ws, headers)

        ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_programs,
            new_count,
            updated_count,
            news_count
        ])

        console.print("[green]✓ Log written[/green]")

    except Exception as e:
        console.print(f"[bold red]Log failed: {e}[/bold red]")