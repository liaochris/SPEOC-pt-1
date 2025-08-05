from bs4 import BeautifulSoup

def parse_residence_county(html):
    """
    Given the rendered search-results HTML, parse and return
    the 'Residence County' value from the first record row.
    """
    soup = BeautifulSoup(html, 'html.parser')
    # find the cell/label that contains 'Residence County'
    label = soup.find(lambda tag: tag.name=='span' and 'Residence County' in tag.text)
    if not label:
        return ''
    # the county text often follows in the next sibling span
    county_span = label.find_next_sibling('span')
    return county_span.text.strip() if county_span else ''