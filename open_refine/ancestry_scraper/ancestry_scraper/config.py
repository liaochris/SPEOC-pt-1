# BASE_SEARCH_URL = "https://www.ancestrylibrary.com/search/collections/61025/?name={name}"
STATE_COLLECTION_URLS = {
    "PA": "https://www.ancestrylibrary.com/search/collections/2497/",
    "MA": "https://guides.library.umass.edu/c.php?g=672399&p=4737619",
    "CT": "https://www.ancestrylibrary.com/search/collections/3537/",
    "MD": "https://www.ancestrylibrary.com/search/collections/3552/",
    "NH": "https://www.ancestrylibrary.com/search/collections/49199/",
    "NJ": "https://www.ancestrylibrary.com/search/collections/2234/",
    "NY": "https://www.ancestrylibrary.com/search/collections/2234/",
    "VA": "https://www.ancestrylibrary.com/search/collections/2234/",
    "DE": "https://www.ancestrylibrary.com/search/collections/61025/"
}

RATE_LIMIT_SECONDS = 2
MAX_RETRIES = 3
TIMEOUT = 10
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
]
OUTPUT_CSV = "results.csv"
CHECKPOINT_FILE = "progress.json"