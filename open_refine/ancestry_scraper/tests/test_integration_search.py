import pytest
from ancestry_scraper.search import fetch_search_page, fetch_search_with_requests
from ancestry_scraper.parser import parse_residence_county

@pytest.mark.integration
def test_integration_fetch_and_parse():
    """
    Integration test: uses existing Chrome profile (with library proxy cookies)
    to fetch a real Ancestry Library search and parse the residence county.
    """
    html, url = fetch_search_page(
        "Thomas McKean",
        event_year=1777,
        year_offset=10
    )
    # URL correctness
    assert "name=Thomas_McKean" in url
    assert "&event=1777" in url
    assert "&event_x=10-0-0" in url
    # Parsed county should be non-empty
    county = parse_residence_county(html)
    assert county, "Expected non-empty residence county"

@pytest.mark.integration
def test_integration_fetch_and_parse_https():
    html, url = fetch_search_with_requests(
        "Thomas McKean",
        event_year=1777,
        year_offset=10
    )

    # 1) URL sanity
    assert "name=Thomas_McKean" in url
    assert "&event=1777" in url
    assert "&event_x=10-0-0" in url

    # 2) Parse county
    county = parse_residence_county(html)
    assert county, "Expected a non-empty residence county"