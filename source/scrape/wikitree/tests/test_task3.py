# tests/test_task3.py
import json, csv
import pandas as pd

from task_3 import run_task3

def fake_get_profile(profile_key):
    # minimal stubs for 2 children
    data = {
        "C-1": {"RealName":"John", "LastNameCurrent":"Smith",
                "BirthLocation":"Philadelphia, Pennsylvania"},
        "C-2": {"RealName":"John", "LastNameCurrent":"Smith",
                "BirthLocation":"Boston, Massachusetts"},
    }
    # Return dict with same keys your code expects
    return data.get(profile_key, {"Name": profile_key})

def test_run_task3(tmp_path):
    # 1) edges json with two child IDs
    edges_path = tmp_path / "edges.json"
    edges = [
        {"parent_id":"P-1", "child_id":"C-1"},
        {"parent_id":"P-2", "child_id":"C-2"},
    ]
    edges_path.write_text(json.dumps(edges), encoding="utf-8")

    # 2) post-1790 CSV with name+state only matching C-1 (PA)
    post_path = tmp_path / "post.csv"
    df = pd.DataFrame({
        "Group Name": ["john smith", "jane doe"],
        "Group State": ["PA", "NY"],
    })
    df.to_csv(post_path, index=False)

    # 3) output path
    out_path = tmp_path / "out.csv"

    # 4) run
    summary = run_task3(str(edges_path), str(post_path), str(out_path), fetch_profile=fake_get_profile)

    # 5) assert summary
    assert summary["total"] == 2
    assert summary["hits"] == 1

    # 6) assert file contents
    rows = list(csv.DictReader(open(out_path, encoding="utf-8")))
    by_id = {r["child_id"]: r for r in rows}
    assert by_id["C-1"]["in_post1790"] == "True" or by_id["C-1"]["in_post1790"] == "YES"
    assert by_id["C-2"]["in_post1790"] == "False" or by_id["C-2"]["in_post1790"] == "NO"