from pathlib import Path

BASE_URL = "https://books.toscrape.com/"
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/your-username/scraper)"
REQUEST_TIMEOUT = 10  # seconds
POLITE_DELAY = 0.6    # delay between live network requests (seconds)

CACHE_DIR = Path("cache")
OUTPUT_DIR = Path("output")
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)