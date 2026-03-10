import requests
import pytest
from source.scrape.wikitree.wikitree import _YearFromDate, SearchProfileKey, GetDescendants, GetPrimaryLocation, SearchCandidatesForName
from source.scrape.wikitree.search_wikitree_candidates import WriteCandidates

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
    assert _YearFromDate("1778-05-12") == 1778
    assert _YearFromDate("c.1778") == 1778
    assert _YearFromDate("born 180") is None
    assert _YearFromDate("") is None

def test_search_profile_key_no_profiles(monkeypatch):
    calls = []
    def fake_get(url, params):
        calls.append(params)
        return DummyResponse({"profiles": []})
    monkeypatch.setattr(requests, "get", fake_get)

    result = SearchProfileKey("Alice", birth_year_range=(1700, 1800))
    assert result is None
    assert calls and calls[0]["action"] == "search"

def test_search_profile_key_filters_and_selects(monkeypatch):
    search_json = {
        "profiles": [
            {"profileKey": "P1"},
            {"profileKey": "P2"},
        ]
    }
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

    best = SearchProfileKey("Bob", birth_year_range=(1700, 1770))
    assert best == "P1"


def test_search_profile_key_out_of_range(monkeypatch):
    def fake_get(url, params):
        if params["action"] == "search":
            return DummyResponse({"profiles": [{"profileKey": "PX"}]})
        else:
            return DummyResponse({"profiles": {"PX": {"birthDate": "1801-01-01"}}})
    monkeypatch.setattr(requests, "get", fake_get)

    assert SearchProfileKey("Charlie", birth_year_range=(1700, 1770)) is None


def test_get_descendants(monkeypatch):
    expected = [{"name": "X"}, {"name": "Y"}]
    def fake_get(url, params):
        assert params["action"] == "getDescendants"
        return DummyResponse({"descendants": expected})
    monkeypatch.setattr(requests, "get", fake_get)

    desc = GetDescendants("ANYKEY", generations=2)
    assert desc == expected

def test_search_and_descendants_benjamin_franklin():
    key = SearchProfileKey(
        "Benjamin Franklin",
        birth_year_range=(1700, 1780),
        max_candidates=100
    )

    assert isinstance(key, str) and key, "Expected a valid profileKey string"

    descs = GetDescendants(key, generations=1)
    assert isinstance(descs, list), "Expected a list of descendants"
    assert all(isinstance(d, dict) and "Id" in d for d in descs), descs
    assert len(descs) >= 1, "Expected at least one known descendant of Benjamin Franklin"

def test_get_primary_location_real_api():
    loc = GetPrimaryLocation(
        "George Washington",
        state="Virginia",
        birth_year_range=(1720, 1740),
        max_candidates=100
    )

    assert isinstance(loc, str) and loc, f"Expected a non-empty location, got {loc!r}"
    assert "Westmoreland" in loc or "Virginia" in loc

def test_search_candidates_for_name():
    out = SearchCandidatesForName(
        name="George Washington",
        state="Virginia"
    )
    print(out)

def test_write_candidates():
    WriteCandidates(
        names_csv="data/test.csv",
        out_csv="results/result.csv"
    )
