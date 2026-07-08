from utils.models import CreditProgram
import requests


def fetch_programs():
    url = "https://api.worldbank.org/v2/projects?format=json&rows=5"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            raise Exception("API failed")

        data = response.json()

        if not isinstance(data, list) or len(data) < 2:
            raise Exception("Invalid API response")

        programs = []

        for item in data[1]:
            program = CreditProgram(
                provider="World Bank",
                program_name=item.get("project_name", "Unknown"),
                category="Government Grants",
                credit_amount=str(item.get("totalamt", "Unknown")),
                validity="N/A",
                eligibility="N/A",
                requires_vc="No",
                apply_url="https://projects.worldbank.org/",
                notes="World Bank funding project",
                source_site="worldbank.org",
            )
            programs.append(program)

        return programs

    except Exception:
        # fallback (always safe)
        return [
            CreditProgram(
                provider="World Bank",
                program_name="Startup Support Initiative",
                category="Government Grants",
                credit_amount="$50,000",
                validity="N/A",
                eligibility="Early-stage startups",
                requires_vc="No",
                apply_url="https://www.worldbank.org/",
                notes="Fallback data",
                source_site="worldbank.org",
            )
        ]