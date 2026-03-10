from source.lib.ancestry_scraper.config import STATE_ABBREVIATIONS

STATE_FULL_TO_ABBR = {v.upper(): k for k, v in STATE_ABBREVIATIONS.items()}
STATE_FULL         = list(STATE_FULL_TO_ABBR.keys())


def Norm(s):
    return s.strip().lower()


def BuildName(p):
    first = p.get("RealName") or p.get("FirstName") or ""
    last  = p.get("LastNameCurrent") or p.get("LastNameAtBirth") or ""
    full  = (f"{first} {last}").strip()
    if not full:
        full = p.get("LongName") or p.get("BirthName") or p.get("Name") or ""
    return full


def ExtractStateCoords(location):
    if not location:
        return ""
    t = location.upper()
    for full in STATE_FULL:
        if full in t:
            return STATE_FULL_TO_ABBR[full]
    return ""
