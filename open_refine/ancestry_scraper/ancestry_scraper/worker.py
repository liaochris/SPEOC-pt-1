from .storage import append_result, load_progress, save_progress
from .search import fetch_search_page
from .parser import parse_residence_county

def process_name(name, event_year=None, event_x=None):
    """
    Orchestrate lookup:
    1. Skip if done.
    2. Fetch search page HTML+URL.
    3. Parse residence county from HTML.
    4. Save [name, url, county] and mark done.
    """
    prog = load_progress()
    if prog.get(name) == 'done': # Skip if done.
        return
    try:
        html, url = fetch_search_page(name, event_year=event_year, event_x=event_x) # Fetch search page HTML+URL.
        county = parse_residence_county(html) # Parse residence county from HTML.
        append_result([name, url, county]) # Save [name, url, county] and mark done.
        prog[name] = 'done'
    except Exception as e:
        prog[name] = f'error: {e}'
    finally:
        save_progress(prog)