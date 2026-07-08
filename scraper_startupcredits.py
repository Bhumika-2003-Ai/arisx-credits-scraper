import requests
from bs4 import BeautifulSoup
import re


URL = "https://startupcredits.dev"


# ✅ Clean + validate program name
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_valid_program(text: str) -> bool:
    if not text or len(text) < 15:
        return False

    text_lower = text.lower()

    # ❌ Remove junk / blog text
    junk_keywords = [
        "how", "guide", "compare", "vs", "review",
        "founder", "every", "most", "yes", "free",
        "credits are", "expire", "loved", "top", "★★★★★"
    ]

    if any(word in text_lower for word in junk_keywords):
        return False

    return True


# ✅ Normalize provider names
def normalize_provider(name: str) -> str:
    mapping = {
        "aws": "AWS",
        "google": "Google",
        "azure": "Microsoft",
        "openai": "OpenAI",
        "github": "GitHub",
        "stripe": "Stripe",
        "digitalocean": "DigitalOcean",
        "vercel": "Vercel",
        "render": "Render"
    }
    return mapping.get(name.lower(), name.capitalize())


def scrape_startupcredits():
    print("Scraping startupcredits.dev...")

    try:
        res = requests.get(URL, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching site: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    programs = []
    seen = set()

    cards = soup.find_all(["div", "section", "li"])

    KEYWORDS = [
        "aws", "google", "azure", "openai",
        "github", "stripe", "digitalocean",
        "vercel", "render"
    ]

    for card in cards:
        text = clean_text(card.get_text(" ", strip=True))

        if not is_valid_program(text):
            continue

        text_lower = text.lower()

        # ✅ Detect provider
        matched_provider = None
        for k in KEYWORDS:
            if k in text_lower:
                matched_provider = normalize_provider(k)
                break

        if not matched_provider:
            continue

        # ✅ Extract better program name (first sentence)
        program_name = text.split(".")[0][:100]

        # ✅ Dedup key
        key = (matched_provider.lower(), program_name.lower())

        if key in seen:
            continue
        seen.add(key)

        programs.append({
            "provider": matched_provider,
            "program_name": program_name,
            "category": "Startup Credits",
            "credit_amount": "Unknown",
            "validity": "Unknown",
            "eligibility": "Unknown",
            "requires_vc": "Unknown",
            "apply_url": URL,
            "notes": text[:200],
            "source_site": "startupcredits.dev"
        })

    print(f"✓ startupcredits.dev: {len(programs)} programs found")
    return programs


# ✅ REQUIRED for pipeline
def scrape():
    return scrape_startupcredits()


# ✅ TEST RUN
if __name__ == "__main__":
    data = scrape_startupcredits()

    if not data:
        print("⚠️ No programs found")

    for item in data[:5]:
        print(item)