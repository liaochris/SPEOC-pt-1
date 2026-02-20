# EDIT_SCRAPE.md — Pending scraper improvements

## 1. Fix town pop URL (`ancestry.com` → `ancestrylibrary.com`)

**File:** `source/scrape/ancestry_town_population_scraper/scrape_town_populations.py:60`

```python
# Current (wrong — public site, may hit paywalls):
census_url = "https://www.ancestry.com/search/collections/5058/"

# Fix:
census_url = "https://www.ancestrylibrary.com/search/collections/5058/"
```

Fix before the next live run. CD and loan office both use `ancestrylibrary.com` (library edition).

---

## 2. Parameterize auth entry point URL

**File:** `source/lib/ancestry_scraper/auth.py:8-9`

```python
# Current (hardcoded to Georgia Tech Galileo proxy):
# TODO: update entry point URL in future step
driver.get("https://www.galileo.usg.edu/express?link=zual&inst=git1")
```

Replace with an environment variable or config value so users at other institutions can set their own proxy URL:

```python
import os
entry_url = os.environ.get("ANCESTRY_PROXY_URL", "https://www.galileo.usg.edu/express?link=zual&inst=git1")
driver.get(entry_url)
```

---

## 3. Automate the auth login flow

**File:** `source/lib/ancestry_scraper/auth.py:12`

```python
# Current: waits up to 5 minutes for a human to complete the proxy redirect
WebDriverWait(driver, 300).until(EC.url_contains("ancestrylibrary.com"))
```

Currently requires manual browser interaction to complete the Okta/SSO redirect. Automating this would require programmatically driving the institution's SSO login (credentials + MFA). Deferred — architecture is correct, just needs credentials injected.

---

## 4. Unify the driver singleton across all three scrapers

**File:** `source/lib/ancestry_scraper/search.py:7-13`

```python
# Current: loan office has its own module-level global driver
_driver = None

def _GetDriver():
    global _driver
    if _driver is None:
        _driver = GetAuthenticatedDriver()
    return _driver
```

CD and town pop each create a driver in `Main()` and pass it through. Loan office owns a separate singleton inside `search.py`. If you want a single auth session shared across all three scrapers (one login instead of three), refactor to pass a single authenticated driver into `FetchSearchPage` rather than using the module global.

---

## 5. Target URLs reference

For understanding which Ancestry collection each scraper hits:

| Scraper | URL | Notes |
|---|---|---|
| Loan office | Per-state from `STATE_COLLECTION_URLS` in `config.py` | PA→2497, CT→3537, MD→3552, DE→61025, NJ/VA→2234, MA/NH/NY→5058+residence |
| CD scraper | `ancestrylibrary.com/search/collections/5058/` | National 1790 census; location pinned via numeric suffix in `LOCATIONSUFFIX` |
| Town pop | `ancestry.com/search/collections/5058/` | **Bug — see item 1 above** |

To add a new state to the loan office, add an entry to `STATE_COLLECTION_URLS` in `source/lib/ancestry_scraper/config.py`.
