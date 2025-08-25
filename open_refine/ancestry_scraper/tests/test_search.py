import pytest
from ancestry_scraper.search import fetch_search_page, _driver

# define a fake Selenium driver
class DummyDriver:
    def __init__(self):
        self.last_url = None
        self.current_url = None
        self.html = "<html><body>ok</body></html>" # return a canned html string

    def get(self, url):
        self.last_url = url 
        self.current_url = url # records the url it was asked to load
    def page_source(self):
        return self.html

@pytest.fixture(autouse=True)
def patch_driver(monkeypatch):
    dummy = DummyDriver()
    monkeypatch.setattr("ancestry_scraper.search._driver", dummy) # replace the real selenium driver with our dummy
    return dummy

def test_fetch_search_page_url_and_html(patch_driver):
    html, url = fetch_search_page("John Doe", "DE", event_year=1800, year_offset=5)
    assert "name=John_Doe" in url
    assert "&event=1800" in url
    # the offset should now be '5-0-0'
    assert "&event_x=5-0-0" in url
    assert html == patch_driver.html