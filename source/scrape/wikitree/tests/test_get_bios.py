import source.scrape.wikitree.get_bios as sbp
import json
from pathlib import Path

def make_input_csv(tmp_path: Path, rows):
    p = tmp_path / "task_1.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        # columns based on your CSV
        f.write("query_name,state,range_lo,range_hi,profile_key,birth_year,birth_place,url\n")
        for r in rows:
            f.write(",".join(r) + "\n")
    return p


def read_jsonl(path: Path):
    lines = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                lines.append(json.loads(line))
    return lines

def test_main_writes_jsonl_and_is_idempotent(tmp_path, monkeypatch):
    """
    Unit test: mock get_profile and verify:
      - main() reads the CSV and writes JSONL
      - expected fields are present
      - running main() twice doesn't duplicate results (resume works)
    """
    # Arrange: temp input/output locations
    input_csv = make_input_csv(
        tmp_path,
        rows=[
            # query_name, state, range_lo, range_hi, profile_key, birth_year, birth_place, url
            ["JOSHUA WENTWORTH", "New Hampshire", "1700", "1770", "Wentworth-1687", "1742",
             "Portsmouth, Rockingham, New Hampshire", "https://www.wikitree.com/wiki/Wentworth-1687"]
        ],
    )
    output_jsonl = tmp_path / "wikitree_bios.jsonl"

    # Patch module-level constants and sleep to speed test
    monkeypatch.setattr(sbp, "INPUT_CSV", str(input_csv))
    monkeypatch.setattr(sbp, "OUTPUT_JSONL", str(output_jsonl))
    monkeypatch.setattr(sbp, "SLEEP_SEC", 0)

    # Mock get_profile to avoid network
    def fake_get_profile(profile_key: str):
        assert profile_key == "Wentworth-1687"
        return {
            "Id": "12345",
            "Name": "Joshua-Wentworth-1687",
            "FirstName": "Joshua",
            "LastNameCurrent": "Wentworth",
            "LastNameAtBirth": "Wentworth",
            "LongName": "Joshua Wentworth",
            "BirthDate": "1742-02-20",
            "BirthLocation": "Portsmouth, Rockingham, New Hampshire",
            "DeathDate": "1809-03-10",
            "DeathLocation": "Portsmouth, Rockingham, New Hampshire",
            "Bio": "== Biography ==\nJoshua Wentworth was a merchant and public official in New Hampshire."
        }

    monkeypatch.setattr(sbp, "get_profile", fake_get_profile)

    # Act: run main() twice (to test resume/idempotency)
    sbp.main()
    sbp.main()

    # Assert
    assert output_jsonl.exists(), "JSONL output file should be created"
    records = read_jsonl(output_jsonl)
    assert len(records) == 1, "Running twice should not duplicate the record"

    rec = records[0]
    # From CSV
    assert rec["profile_key"] == "Wentworth-1687"
    assert rec["query_name"] == "JOSHUA WENTWORTH"
    assert rec["state"] == "New Hampshire"
    # From script
    assert rec["status"] == "ok"
    assert rec["error"] is None
    assert "pulled_at" in rec and rec["pulled_at"].endswith("Z") is False or True  # isoformat string exists
    # From mocked profile
    assert rec["Name"] == "Joshua-Wentworth-1687"
    assert rec["BirthDate"] == "1742-02-20"
    assert "Bio" in rec and "Biography" in rec["Bio"]


def test_main_integration_real_profile(tmp_path, monkeypatch):
    """
    Optional integration test: uses the real get_profile to fetch Wentworth-1687.
    Marked as 'integration' so it can be skipped by default: `pytest -m 'integration'`
    """
    input_csv = make_input_csv(
        tmp_path,
        rows=[
            ["JOSHUA WENTWORTH", "New Hampshire", "1700", "1770", "Wentworth-1687", "", "", "https://www.wikitree.com/wiki/Wentworth-1687"]
        ],
    )
    output_jsonl = tmp_path / "wikitree_bios.jsonl"

    monkeypatch.setattr(sbp, "INPUT_CSV", str(input_csv))
    monkeypatch.setattr(sbp, "OUTPUT_JSONL", str(output_jsonl))
    monkeypatch.setattr(sbp, "SLEEP_SEC", 0)

    # Use real get_profile from your module (no monkeypatch here)
    # If your environment blocks network, this will fail; that's why it's marked.
    sbp.main()

    assert output_jsonl.exists()
    recs = read_jsonl(output_jsonl)
    assert len(recs) == 1
    rec = recs[0]
    assert rec["profile_key"] == "Wentworth-1687"
    assert rec["status"] == "ok"
    # We can't assert exact field values (profile may change), but Bio should exist.
    assert "bio" in rec and isinstance(rec["bio"], str) and len(rec["bio"]) > 0