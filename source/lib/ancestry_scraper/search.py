from .config import STATE_COLLECTION_URLS
from .session import RateLimited
from .auth import GetAuthenticatedDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

_driver = None

def _GetDriver():
    global _driver
    if _driver is None:
        _driver = GetAuthenticatedDriver()
    return _driver

@RateLimited
def FetchSearchPage(name, state, event_year=None, year_offset=0, name_x="1_1"):
    """
    Build the library search URL, navigate via Selenium,
    wait for page load, and return the rendered HTML and URL.

    - name: e.g. 'Thomas McKean'
    - event_year: e.g. 1777
    - year_offset: e.g. 10
    """

    spec = STATE_COLLECTION_URLS[state.upper()]
    base = spec["base"]

    formatted = name.replace(" ", "_")
    url = f"{base}?name={formatted}"
    if event_year:
        url += f"&event={event_year}"
        if year_offset:
            url += f"&event_x={year_offset}-0-0"

    res = spec.get("residence")
    if res:
        url += f"&residence={res}&residence_x=_1-0"

    url += f"&name_x={name_x}"
    driver = _GetDriver()
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.url_contains(f"name={formatted}")
    )

    raw = driver.page_source
    if callable(raw):
        raw = raw()

    return raw, _driver.current_url
