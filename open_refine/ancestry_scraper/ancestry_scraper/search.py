import time
from .config import BASE_SEARCH_URL
from .session import rate_limited, get_library_session
from .auth import get_authenticated_driver

# reuse one logged-in Selenium driver across calls
# _driver = get_authenticated_driver()
_driver = None

def _get_driver():
    global _driver
    if _driver is None:
        _driver = get_authenticated_driver() # only now we launch Chrome
    return _driver

@rate_limited
def fetch_search_page(name, event_year=None, year_offset=0):

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
    url = BASE_SEARCH_URL.format(name=formatted)
    if event_year:
        url += f"&event={event_year}"
        if year_offset:
            url += f"&event_x={year_offset}-0-0"
    # navigate to URL
    driver = _get_driver()
    driver.get(url)
    time.sleep(1.5)  # allow dynamic content to load
    # return page HTML and actual URL

    raw = driver.page_source
    if callable(raw):
        raw = raw()

    return raw, _driver.current_url


@rate_limited
def fetch_search_with_requests(name, event_year=None, year_offset=0):
    """
    Build the search URL just as before, then GET it with requests,
    using the pre-authenticated Library session.
    Returns: (html_text, used_url)
    """
    formatted = name.replace(" ", "_")
    url = BASE_SEARCH_URL.format(name=formatted)
    if event_year:
        url += f"&event={event_year}"
        if year_offset:
            url += f"&event_x={year_offset}-0-0"

    session = get_library_session()
    resp = session.get(url, timeout=10, allow_redirects=True)
    resp.raise_for_status()
    return resp.text, resp.url