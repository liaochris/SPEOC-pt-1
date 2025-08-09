import pytest
from ancestry_scraper.search import fetch_search_page
from ancestry_scraper.parser import parse_residence_county

@pytest.mark.integration
def test_integration_fetch_and_parse():
    """
    Integration test: uses existing Chrome profile (with library proxy cookies)
    to fetch a real Ancestry Library search and parse the residence county.
    """
    html, url = fetch_search_page(
        "Robert Livingston",
        "NY",
        event_year=1777,
        year_offset=10
    )
    # URL correctness
    assert "name=Robert_Livingston" in url
    assert "&event=1777" in url
    assert "&event_x=10-0-0" in url
    # Parsed county should be non-empty
    county = parse_residence_county(html)
    assert "New York" == county
    # assert county, "Expected non-empty residence county"