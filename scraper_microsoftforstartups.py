from rich.console import Console

console = Console()

def scrape():
    console.print("[cyan]Scraping Microsoft for Startups...[/cyan]")
    return [{"provider": "Microsoft", "credits": "$150,000 Azure Credits"}]

if __name__ == "__main__":
    data = scrape()
    print(data)