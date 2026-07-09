# ⚡ ArisX Startup Credits Scraper

Automated scraper that aggregates startup credit programs (AWS, Anthropic, Google Cloud, OpenAI, Deepgram, etc.) and syncs them to Google Sheets with deduplication, news updates, and run logs.

---

## Features

- Scrapes startup credit programs
- Google Sheets integration
- Recent News tab
- Run Log tab
- Deduplication (no duplicate rows)
- SQLite database
- 24-hour scheduler support

---

## Project Structure

```
arisx-credits-scraper/
│── scrapers/
│── sheets/
│── db/
│── screenshots/
│── run.py
│── requirements.txt
│── README.md
│── .env.example
│── .gitignore
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Bhumika-2003-Ai/arisx-credits-scraper.git
cd arisx-credits-scraper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file using `.env.example`.

Example:

```env
GOOGLE_SERVICE_ACCOUNT_JSON=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id
NEWS_API_KEY=your_news_api_key
```

Place your `credentials.json` file in the project root.

---

## Google Sheets Setup

1. Create a Google Cloud Project.
2. Enable Google Sheets API.
3. Enable Google Drive API.
4. Create a Service Account.
5. Download `credentials.json`.
6. Share your Google Sheet with the Service Account email as **Editor**.
7. Copy the Sheet ID into your `.env` file.

---

## Run

Run once:

```bash
python run.py
```

```bash
python run.py --now
```

Run daily:

```bash
python run.py --schedule
```

---

## Screenshots

### Credits Tracker

![Credits](screenshots/credits.jpg)

### Recent News

![News](screenshots/news.jpg)

### Run Log

![Run Log](screenshots/log.jpg)

---

## Technologies

- Python
- BeautifulSoup
- Requests
- SQLite
- Google Sheets API
- Feedparser

---

## Notes

- `.env` is not committed.
- `credentials.json` is not committed.
- `.env.example` contains placeholder values only.
- Duplicate startup programs are automatically removed.

---

## Repository

https://github.com/Bhumika-2003-Ai/arisx-credits-scraper
