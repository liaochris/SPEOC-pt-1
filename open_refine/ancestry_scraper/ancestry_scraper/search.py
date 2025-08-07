# old: from .config import BASE_SEARCH_URL
from .config import STATE_COLLECTION_URLS
from .session import rate_limited
from .auth import get_authenticated_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# reuse one logged-in Selenium driver across calls
# _driver = get_authenticated_driver()
_driver = None

def _get_driver():
    global _driver
    if _driver is None:
        _driver = get_authenticated_driver() # only now we launch Chrome
    return _driver

@rate_limited
def fetch_search_page(name, state, event_year=None, year_offset=0):
    """
    Build the library search URL, navigate via Selenium,
    wait for page load, and return the rendered HTML and URL.

    - name: e.g. 'Thomas McKean'
    - event_year: e.g. 1777
    - event_x: e.g. '10-0-0'
    """
    # format name for URL (spaces->underscores)
    formatted = name.replace(" ", "_")
    # build URL
    base = STATE_COLLECTION_URLS[state.upper()]
    formatted = name.replace(" ", "_")
    url = f"{base}?name={formatted}"
    # old: url = BASE_SEARCH_URL.format(name=formatted)
    if event_year:
        url += f"&event={event_year}"
        if year_offset:
            url += f"&event_x={year_offset}-0-0"

    url += "&name_x=1_1"
    # navigate to URL
    driver = _get_driver()
    driver.get(url)
    # time.sleep(1.5)  # allow dynamic content to load

    # block until the browser's address bar actually contains your “name=” param
    WebDriverWait(driver, 10).until(
        EC.url_contains(f"name={formatted}")
    )

    # return page HTML and actual URL

    raw = driver.page_source
    if callable(raw):
        raw = raw()

    return raw, _driver.current_url
