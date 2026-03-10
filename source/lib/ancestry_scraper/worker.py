from .storage import AppendResult, LoadProgress, SaveProgress
from .scraper import ScrapeLoanOffice


def ProcessName(name, state, event_year=None):
    prog = LoadProgress(state)
    if prog.get(name) == 'done':
        return
    try:
        result = ScrapeLoanOffice(name, state, event_year)
        AppendResult([name, event_year, result.match_strategy, result.year_offset, result.url, result.match_status, "|".join(result.counties)], state)
        prog[name] = 'done'
    except Exception as e:
        prog[name] = f'error: {e}'
    finally:
        SaveProgress(prog, state)
