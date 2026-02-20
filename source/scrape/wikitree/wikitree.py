from pathlib import Path
import csv
import requests
import re
import logging

log = logging.getLogger(__name__)

INDIR_DERIVED = Path("output/derived/pre1790")
WIKITREE_API = "https://api.wikitree.com/api.php"


def Main():
    with open(INDIR_DERIVED / "loan_office_certificates_cleaned.csv") as f:
        for row in csv.DictReader(f):
            name = row["raw_name"]
            state = row["state"]
            cert_year = int(row["Year"])
            yr0 = cert_year - 90
            yr1 = cert_year - 20
            key = SearchProfileKey(name, state=state, birth_year_range=(yr0, yr1))
            if not key:
                print("No match:", name, "in range", yr0, "-", yr1)
                continue
            descs = GetDescendants(key)
            print(f"{name} ({key}): {len(descs)} descendants")


def YearFromDate(s):
    m = re.search(r"(\d{4})", s)
    return int(m.group(1)) if m else None


def SearchProfileKey(name, state=None, birth_year_range=(1700, 1770), max_candidates=5):
    parts = name.split()
    if len(parts) < 2:
        return None
    fn, ln = parts[0], parts[-1]
    start, end = birth_year_range
    mid = (start + end) // 2
    spread = end - start
    params = {
        "action": "searchPerson",
        "format": "json",
        "FirstName": fn,
        "LastName": ln,
        "limit": max_candidates,
        "BirthLocation": state,
        "fields": "Id,Name,BirthDate",
        "BirthDate": f"{mid}-00-00",
        "dateInclude": "both",
        "dateSpread": str(spread)
    }
    r = requests.get(WIKITREE_API, params=params)
    r.raise_for_status()
    data = r.json()
    log.debug("data: %r", data)
    if not data or "matches" not in data[0]:
        return None
    matches = data[0].get("matches", [])
    good = []
    for m in matches:
        bd = m.get("BirthDate")
        if bd:
            yr = YearFromDate(bd)
            if yr and birth_year_range[0] <= yr <= birth_year_range[1]:
                good.append((m["Name"], yr))
    if not good:
        return None
    mid = sum(birth_year_range) / 2
    good.sort(key=lambda kv: abs(kv[1] - mid))
    return str(good[0][0])


def GetDescendants(profile_key, generations=3):
    r = requests.get(WIKITREE_API, params={
        "action": "getDescendants",
        "format": "json",
        "key": profile_key,
        "depth": generations,
    })
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        return []
    wrapper = data[0]
    return [dict(d) for d in wrapper.get("descendants", [])]


def GetProfile(profile_key):
    resp = requests.get(WIKITREE_API, params={
        "action": "getProfile",
        "format": "json",
        "key": profile_key,
        "fields": "Id,Name,BirthDate,RealName,FirstName,LastNameCurrent,LastNameAtBirth,LongName,"
                  "BirthName,BirthLocation,DeathDate,DeathLocation,Children,Children.Name,"
                  "Children.BirthDate,Children.BirthLocation,Bio",
        "bioFormat": "wiki"
    })
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list) and data:
        return data[0].get("profile", {})
    return {}


def GetProfileForName(name, state=None, birth_year_range=(1700, 1770), max_candidates=5):
    key = SearchProfileKey(name, state=state, birth_year_range=birth_year_range, max_candidates=max_candidates)
    log.debug("key: %r", key)
    if not key:
        return {}
    return GetProfile(key)


def GetPrimaryLocation(name, state=None, birth_year_range=(1700, 1770), max_candidates=5):
    prof = GetProfileForName(name, state, birth_year_range, max_candidates)
    log.debug("profile data: %r", prof)
    if not prof:
        return None
    return prof.get("BirthLocation") or prof.get("DeathLocation")


def SearchCandidatesForName(name, state=None, birth_year_range=(1700, 1770), max_candidates=10):
    parts = name.split()
    if len(parts) < 2:
        return []
    fn = " ".join(parts[:-1])
    ln = parts[-1]
    start, end = birth_year_range
    mid = (start + end) // 2
    params = {
        "action": "searchPerson",
        "format": "json",
        "FirstName": fn,
        "LastName": ln,
        "limit": max_candidates,
        "BirthLocation": state,
        "fields": "Id,Name,BirthDate,BirthLocation,Url",
        "BirthDate": f"{mid}-00-00",
        "dateInclude": "both",
        "dateSpread": str(20),
    }
    r = requests.get(WIKITREE_API, params=params)
    r.raise_for_status()
    data = r.json()
    matches = []
    if isinstance(data, list) and data:
        matches = data[0].get("matches", [])
    out = []
    for m in matches:
        bd = m.get("BirthDate") or ""
        by = YearFromDate(bd)
        if by is None:
            continue
        if not (start <= by <= end):
            continue
        bp = (m.get("BirthLocation") or "")
        if state and (state.lower() not in bp.lower()):
            continue
        out.append({
            "query_name": name,
            "state": state,
            "range_lo": start,
            "range_hi": end,
            "profile_key": m.get("Name"),
            "birth_year": by,
            "birth_place": bp,
            "url": m.get("Url"),
        })
    return out


if __name__ == "__main__":
    Main()
