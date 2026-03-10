from bs4 import BeautifulSoup
import re

def ParseResidenceCounty(html):
    """
    Given the rendered search-results HTML, parse and return
    the 'Residence County' value from the first record row.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Try table-based approach: look for <td data-label="Residence County">
    county = ""
    county_cell = soup.find('td', { 'data-label': re.compile(r'(county|place)',   re.I) })
    if county_cell:
        return county_cell.get_text(strip=True)
    else:
        # Fallback: find a span label containing 'Residence County'
        label = soup.find(lambda tag: tag.name == 'span' and re.search(r'(county|place)', tag.get_text(), re.I))
        if label:
            county_span = label.find_next_sibling('span')
            if county_span:
                return county_span.get_text(strip=True)

    return county


def ParseAllResidenceCounties(html):
    soup = BeautifulSoup(html, 'html.parser')
    cells = soup.find_all('td', {'data-label': re.compile(r'(county|place)', re.I)})
    if cells:
        return list(dict.fromkeys(c.get_text(strip=True) for c in cells))
    labels = soup.find_all(lambda tag: tag.name == 'span' and re.search(r'(county|place)', tag.get_text(), re.I))
    results = []
    for label in labels:
        sibling = label.find_next_sibling('span')
        if sibling:
            results.append(sibling.get_text(strip=True))
    return list(dict.fromkeys(results))