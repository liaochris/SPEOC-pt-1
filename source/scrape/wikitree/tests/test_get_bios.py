import source.scrape.wikitree.get_bios as sbp
import json
from pathlib import Path

def make_input_csv(tmp_path: Path, rows):
    p = tmp_path / "task_1.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
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
    input_csv = make_input_csv(
        tmp_path,
        rows=[
            ["JOSHUA WENTWORTH", "New Hampshire", "1700", "1770", "Wentworth-1687", "1742",
             "Portsmouth, Rockingham, New Hampshire", "https://www.wikitree.com/wiki/Wentworth-1687"]
        ],
    )
    output_jsonl = tmp_path / "wikitree_bios.jsonl"

    monkeypatch.setattr(sbp, "INPUT_CSV", str(input_csv))
    monkeypatch.setattr(sbp, "OUTPUT_JSONL", str(output_jsonl))
    monkeypatch.setattr(sbp, "SLEEP_SEC", 0)

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

    monkeypatch.setattr(sbp, "GetProfile", fake_get_profile)

    sbp.Main()
    sbp.Main()

    assert output_jsonl.exists(), "JSONL output file should be created"
    records = read_jsonl(output_jsonl)
    assert len(records) == 1, "Running twice should not duplicate the record"

    rec = records[0]
    assert rec["profile_key"] == "Wentworth-1687"
    assert rec["query_name"] == "JOSHUA WENTWORTH"
    assert rec["state"] == "New Hampshire"
    assert rec["status"] == "ok"
    assert rec["error"] is None
    assert "pulled_at" in rec
    assert rec["Name"] == "Joshua-Wentworth-1687"
    assert rec["BirthDate"] == "1742-02-20"
    assert "Bio" in rec and "Biography" in rec["Bio"]


def test_main_integration_real_profile(tmp_path, monkeypatch):
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

    sbp.Main()

    assert output_jsonl.exists()
    recs = read_jsonl(output_jsonl)
    assert len(recs) == 1
    rec = recs[0]
    assert rec["profile_key"] == "Wentworth-1687"
    assert rec["status"] == "ok"
    assert "bio" in rec and isinstance(rec["bio"], str) and len(rec["bio"]) > 0
