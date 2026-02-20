STATE_ABBREVIATIONS = {
    'CT': 'Connecticut', 'DE': 'Delaware', 'GA': 'Georgia', 'MA': 'Massachusetts',
    'MD': 'Maryland', 'ME': 'Maine', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NY': 'New York', 'NC': 'North Carolina', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'VA': 'Virginia', 'VT': 'Vermont'
}

# BASE_SEARCH_URL = "https://www.ancestrylibrary.com/search/collections/61025/?name={name}"
STATE_COLLECTION_URLS = {
    "PA": {
        "base":"https://www.ancestrylibrary.com/search/collections/2497/",
        "residence":None
    },
    "MA": {
        "base":"https://www.ancestrylibrary.com/search/collections/5058",
        "residence":"_massachusetts-usa_24"
    },
    "CT": {
        "base":"https://www.ancestrylibrary.com/search/collections/3537/",
        "residence":None
    },
    "MD": {
        "base":"https://www.ancestrylibrary.com/search/collections/3552/",
        "residence":None
    },
    "NH": {
        "base":"https://www.ancestrylibrary.com/search/collections/5058",
        "residence":"_new+hampshire-usa_32"
    },
    "NJ": {
        "base":"https://www.ancestrylibrary.com/search/collections/2234/",
        "residence":"_new+jersey-usa_33"
    },
    "NY": {
        "base":"https://www.ancestrylibrary.com/search/collections/5058",
        "residence":"_new+york-usa_35"
    },
    "VA": {
        "base":"https://www.ancestrylibrary.com/search/collections/2234/",
        "residence":"_virginia-usa_49"
    },
    "DE": {
        "base":"https://www.ancestrylibrary.com/search/collections/61025/",
        "residence":None
    }
}

NAME_X_STRATEGIES = ["1_1", "s_s", "ps_ps"]
YEAR_OFFSETS = [0, 1, 3]

RATE_LIMIT_SECONDS = 2
MAX_RETRIES = 3
TIMEOUT = 10
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
]