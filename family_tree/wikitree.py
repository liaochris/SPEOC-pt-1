import csv
import requests
import re
from typing import Optional, Dict
import logging
log = logging.getLogger(__name__)

WIKITREE_API = "https://api.wikitree.com/api.php"

def _year_from_date(s: str) -> Optional[int]:
    """Extract a 4-digit year from strings like '1778-05-12' or 'c.1778'."""
    m = re.search(r"(\d{4})", s)
    return int(m.group(1)) if m else None

def search_profile_key(name, state=None, birth_year_range=(1700,1770), max_candidates=5):
    # split into first/last
    parts = name.split()
    if len(parts) < 2:
        return None
    fn, ln = parts[0], parts[-1]

    start, end = birth_year_range
    # midpoint year for “target”
    mid = (start + end) // 2
    # how many years on either side
    spread = end - start

    params = {
        "action":       "searchPerson",
        "format":       "json",
        "FirstName":    fn,
        "LastName":     ln,
        "limit":        max_candidates,
        "BirthLocation": state,
        "fields":       "Id,Name,BirthDate",
        "BirthDate":    f"{mid}-00-00",
        "dateInclude":  "both", 
        "dateSpread": str(spread)
    }
    # optional: params["BirthLocation"] = state

    r = requests.get(WIKITREE_API, params=params)
    r.raise_for_status()
    data = r.json()
    log.debug("data: %r", data)

    if not data or "matches" not in data[0]:
        return None

    # collect (profileKey, year) for those in range
    matches = data[0].get("matches", [])
    good = []
    for m in matches:
        bd = m.get("BirthDate")
        if bd:
            yr = _year_from_date(bd)
            if yr and birth_year_range[0] <= yr <= birth_year_range[1]:
                good.append((m["Name"], yr))

    if not good:
        return None

    # pick the one closest to the midpoint
    mid = sum(birth_year_range)/2
    good.sort(key=lambda kv: abs(kv[1] - mid))
    return str(good[0][0])

def get_descendants(profile_key, generations=3):
    r = requests.get(WIKITREE_API, params={
        "action":      "getDescendants",
        "format":      "json",
        "key":  profile_key,
        "depth": generations,
    })
    r.raise_for_status()
    data = r.json()

    if not isinstance(data, list) or not data:
        return []

    wrapper = data[0]
    raw_descs = wrapper.get("descendants", [])
    out = []
    for d in raw_descs:
        # Copy over everything, and normalize Id → profileKey
        normalized = dict(d)
        out.append(normalized)

    return out

def get_profile(profile_key: str) -> Dict[str,str]:
    """
    Fetch the chosen person’s profile, including location fields.
    Returns the first element of the response (a dict of fields → values).
    """
    resp = requests.get(WIKITREE_API, params={
        "action": "getProfile",
        "format": "json",
        "key":     profile_key,
        "fields":  "Id,Name,BirthDate,BirthLocation,DeathDate,DeathLocation"
    })
    resp.raise_for_status()
    data = resp.json()
    
    # getProfile returns a one‐item list of wrapper dicts:
    #   [{ "page_name": ..., "profile": { Id, Name, BirthDate, BirthLocation, … }, "status": 0 }]
    if isinstance(data, list) and data:
        wrapper = data[0]
        return wrapper.get("profile", {})   # ← return the inner profile dict
    
    return {}

def get_profile_for_name(
    name: str,
    state: Optional[str] = None,
    birth_year_range: tuple[int,int] = (1700,1770),
    max_candidates: int = 5
) -> dict:
    """
    1) pick the best matching profileKey for `name` in the given birth_year_range  
    2) fetch that profile via get_profile
    """
    key = search_profile_key(
        name,
        state=state,
        birth_year_range=birth_year_range,
        max_candidates=max_candidates,
    )

    log.debug("key: %r", key)

    if not key:
        return {}
    return get_profile(key)

def get_primary_location(
    name: str,
    state: Optional[str] = None,
    birth_year_range: tuple[int,int] = (1700,1770),
    max_candidates: int = 5) -> Optional[str]:
    """
    Pick one location field to represent “where they lived”.
    Here we prefer BirthLocation, then DeathLocation if birth is missing.
    """
    prof = get_profile_for_name(name, state, birth_year_range, max_candidates)

    log.debug("profile data: %r", prof)

    if not prof:
        return None
    return prof.get("BirthLocation") or prof.get("DeathLocation")

if __name__ == "__main__":
    with open("../data/loan_office_certificates_cleaned.csv") as f:
        for row in csv.DictReader(f):
            name  = row["raw_name"]
            state = row["state"]
            # pick a generous birth‐year window around your certificate “Year”
            cert_year = int(row["Year"])
            yr0 = cert_year - 90
            yr1 = cert_year
            key = search_profile_key(name, state=state, birth_year_range=(yr0,yr1))
            if not key:
                print("❌", name, "→ no profile in range", yr0, "–", yr1)
                continue

            descs = get_descendants(key)
            print(f"✅ {name} ({key}): {len(descs)} descendants")