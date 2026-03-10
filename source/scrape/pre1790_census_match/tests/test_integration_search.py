import pytest
from source.lib.ancestry_scraper.search import FetchSearchPage
from source.lib.ancestry_scraper.parser import ParseResidenceCounty

@pytest.mark.integration
def test_integration_fetch_and_parse():
    """
    Integration test: uses existing Chrome profile (with library proxy cookies)
    to fetch a real Ancestry Library search and parse the residence county.
    """
    html, url = FetchSearchPage(
        "Joseph Albree",
        "NH",
        event_year=1790,
        year_offset=10
    )
    assert "name=Joseph_Albree" in url
    assert "&event=1790" in url
    assert "&event_x=10-0-0" in url
    county = ParseResidenceCounty(html)
    assert "Acworth, Cheshire,New Hampshire" == county
