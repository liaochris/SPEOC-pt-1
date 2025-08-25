import requests
import pytest
from wikitree import _year_from_date, search_profile_key, get_descendants, get_primary_location, search_candidates_for_name
from task_1 import task1_write_candidates

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")

    def json(self):
        return self._json

def test_year_from_date_valid_and_invalid():
    assert _year_from_date("1778-05-12") == 1778
    assert _year_from_date("c.1778") == 1778
    assert _year_from_date("born 180") is None
    assert _year_from_date("") is None

def test_search_profile_key_no_profiles(monkeypatch):
    # simulate search returning no profiles
    calls = []
    def fake_get(url, params):
        calls.append(params)
        return DummyResponse({"profiles": []})
    monkeypatch.setattr(requests, "get", fake_get)

    result = search_profile_key("Alice", birth_year_range=(1700, 1800))
    assert result is None
    # should have only called search
    assert calls and calls[0]["action"] == "search"

def test_search_profile_key_filters_and_selects(monkeypatch):
    # 1) first call: search → two candidates
    search_json = {
        "profiles": [
            {"profileKey": "P1"},
            {"profileKey": "P2"},
        ]
    }
    # 2) next two calls: getProfile for P1, P2
    profile_data = {
        "P1": {"birthDate": "1750-01-01"},
        "P2": {"birthDate": "1760-06-30"},
    }

    call_index = {"i": 0}
    def fake_get(url, params):
        act = params["action"]
        if act == "search":
            call_index["i"] += 1
            return DummyResponse(search_json)
        elif act == "getProfile":
            key = params["profileKey"]
            return DummyResponse({"profiles": {key: profile_data[key]}})
        else:
            pytest.skip(f"Unexpected action {act}")
    monkeypatch.setattr(requests, "get", fake_get)

    # pick middle of 1700–1770 = 1735; P1 is |1750−1735|=15, P2 is |1760−1735|=25 → choose P1
    best = search_profile_key("Bob", birth_year_range=(1700, 1770))
    assert best == "P1"


def test_search_profile_key_out_of_range(monkeypatch):
    # search returns one candidate but birthDate is outside window
    def fake_get(url, params):
        if params["action"] == "search":
            return DummyResponse({"profiles": [{"profileKey": "PX"}]})
        else:
            return DummyResponse({"profiles": {"PX": {"birthDate": "1801-01-01"}}})
    monkeypatch.setattr(requests, "get", fake_get)

    assert search_profile_key("Charlie", birth_year_range=(1700, 1770)) is None


def test_get_descendants(monkeypatch):
    # simulate getDescendants returning a list
    expected = [{"name": "X"}, {"name": "Y"}]
    def fake_get(url, params):
        assert params["action"] == "getDescendants"
        return DummyResponse({"descendants": expected})
    monkeypatch.setattr(requests, "get", fake_get)

    desc = get_descendants("ANYKEY", generations=2)
    assert desc == expected

def test_search_and_descendants_benjamin_franklin():
    # 1) Search for Benjamin Franklin (born 1706)
    key = search_profile_key(
        "Benjamin Franklin",
        birth_year_range=(1700, 1780),
        max_candidates=100
    )

    assert isinstance(key, str) and key, "Expected a valid profileKey string"

    # 2) Fetch his immediate descendants
    descs = get_descendants(key, generations=1)
    assert isinstance(descs, list), "Expected a list of descendants"
    # each descendant should be a dict with at least a profileKey
    assert all(isinstance(d, dict) and "Id" in d for d in descs), descs

    # 3) Spot-check that we got at least one child
    assert len(descs) >= 1, "Expected at least one known descendant of Benjamin Franklin"

def test_get_primary_location_real_api():
    loc = get_primary_location(
        "George Washington",
        state="Virginia",
        birth_year_range=(1720,1740),
        max_candidates=100
    )

    # We expect at least a non‐empty string mentioning "Virginia"
    assert isinstance(loc, str) and loc, f"Expected a non‐empty location, got {loc!r}"
    assert "Westmoreland" in loc or "Virginia" in loc

def test_search_candidates_for_name():
    out = search_candidates_for_name(
        name="George Washington",
        state="Virginia"
    )

    print(out)

def test_task1_write_candidates():
    task1_write_candidates(
        names_csv="data/test.csv",
        out_csv="results/result.csv"
    )



    