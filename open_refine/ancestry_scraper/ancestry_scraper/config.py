BASE_SEARCH_URL = "https://www.ancestrylibrary.com/search/records?name={name}"
RATE_LIMIT_SECONDS = 2
MAX_RETRIES = 3
TIMEOUT = 10
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
]
OUTPUT_CSV = "results.csv"
CHECKPOINT_FILE = "progress.json"