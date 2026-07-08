from utils.models import CreditProgram
import requests


def fetch_programs():
    try:
        url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(url, timeout=10)
        data = response.json()

        programs = []

        for item in data[:10]:
            program = CreditProgram(
                provider="Mock API",
                program_name=item.get("title", "Unknown"),
                category="Test Data",
                credit_amount="0",
                validity="N/A",
                eligibility="N/A",
                requires_vc="No",
                apply_url=f"https://jsonplaceholder.typicode.com/posts/{item.get('id')}",
                notes="Sample placeholder data",
                source_site="jsonplaceholder.typicode.com",
            )
            programs.append(program)

        return programs

    except Exception as e:
        print(f"Mock scraper error: {e}")
        return []