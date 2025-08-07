from bs4 import BeautifulSoup
import re
from typing import Tuple, Optional

def parse_residence_county(html):
    """
    Given the rendered search-results HTML, parse and return
    the 'Residence County' value from the first record row.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Try table-based approach: look for <td data-label="Residence County">
    county = ""
    county_cell = soup.find('td', { 'data-label': 'Residence County' })
    if county_cell:
        return county_cell.get_text(strip=True)
    else:
        # Fallback: find a span label containing 'Residence County'
        label = soup.find(lambda tag: tag.name == 'span' and 'Residence County' in tag.get_text())
        if label:
            county_span = label.find_next_sibling('span')
            if county_span:
                return county_span.get_text(strip=True)

    return county