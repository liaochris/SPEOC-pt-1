from ancestry_scraper.parser import parse_residence_county

def test_parse_residence_county_present():
    html = """
      <span>Residence County</span>
      <span>Greene County</span>
    """
    county = parse_residence_county(html)  # should return back county 
    assert county == "Greene County"

def test_parse_residence_county_missing():
    html = "<html><body>No label here</body></html>"
    assert parse_residence_county(html) == ""