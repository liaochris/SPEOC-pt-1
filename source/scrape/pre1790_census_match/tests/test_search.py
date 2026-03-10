import pytest
from source.lib.ancestry_scraper.search import FetchSearchPage

class DummyDriver:
    def __init__(self):
        self.last_url = None
        self.current_url = None
        self.html = "<html><body>ok</body></html>"

    def get(self, url):
        self.last_url = url
        self.current_url = url
    def page_source(self):
        return self.html

@pytest.fixture(autouse=True)
def patch_driver(monkeypatch):
    dummy = DummyDriver()
    monkeypatch.setattr("source.lib.ancestry_scraper.search._driver", dummy)
    return dummy

def test_fetch_search_page_url_and_html(patch_driver):
    html, url = FetchSearchPage("John Doe", "DE", event_year=1800, year_offset=5)
    assert "name=John_Doe" in url
    assert "&event=1800" in url
    assert "&event_x=5-0-0" in url
    assert html == patch_driver.html

def test_fetch_search_page_name_x(patch_driver):
    html, url = FetchSearchPage("John Doe", "DE", event_year=1800, year_offset=5, name_x="s_s")
    assert "&name_x=s_s" in url

def test_fetch_search_page_name_x_default(patch_driver):
    html, url = FetchSearchPage("John Doe", "DE", event_year=1800, year_offset=5)
    assert "&name_x=1_1" in url
