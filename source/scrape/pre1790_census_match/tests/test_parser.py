from source.lib.ancestry_scraper.parser import ParseResidenceCounty, ParseAllResidenceCounties

def test_parse_residence_county_present():
    html = """
      <span>Residence County</span>
      <span>Greene County</span>
    """
    county = ParseResidenceCounty(html)
    assert county == "Greene County"

def test_parse_residence_county_missing():
    html = "<html><body>No label here</body></html>"
    assert ParseResidenceCounty(html) == ""

def test_parse_all_residence_counties_multiple():
    html = """
      <td data-label="Residence County">Greene County</td>
      <td data-label="Residence County">Adams County</td>
    """
    counties = ParseAllResidenceCounties(html)
    assert "Greene County" in counties
    assert "Adams County" in counties

def test_parse_all_residence_counties_empty():
    html = "<html><body>No label here</body></html>"
    assert ParseAllResidenceCounties(html) == []
