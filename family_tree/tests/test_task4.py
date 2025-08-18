import json
import pandas as pd

import task_4 as mod  # import your script/module

def test_refine_matches_keep_missing_years(tmp_path, monkeypatch):
    """
    When drop_if_missing_year=False:
      - Keep rows with missing BirthDate
    """
    def fake_get_profile(profile_key: str):
        mapping = {
            "C_OK": {"BirthDate": "1750-03-15"},  # inside window
            "C_MISSING": {},                      # missing birth year
        }
        return mapping.get(profile_key, {})

    monkeypatch.setattr(mod, "get_profile", fake_get_profile)

    in_csv = tmp_path / "task_3_matches.csv"
    pd.DataFrame(
        [
            {"child_id": "C_OK",      "child_name": "A Person", "state": "PA", "in_post1790": True, "error": ""},
            {"child_id": "C_MISSING", "child_name": "B Person", "state": "MA", "in_post1790": True, "error": ""},
        ]
    ).to_csv(in_csv, index=False)

    out_csv = tmp_path / "filtered.csv"

    filtered = mod.refine_matches(
        in_csv=str(in_csv),
        out_csv=str(out_csv),
        center_year=1760,
        window=20,
        drop_if_missing_year=False,  # keep missing
    )

    df_out = pd.read_csv(out_csv)
    # Both should be kept: one by year match, one due to missing allowed
    assert len(filtered) == 2
    assert set(df_out["child_id"]) == {"C_OK", "C_MISSING"}

def test_refine_matches_defaults(tmp_path, monkeypatch):
    """
    Default behavior:
      - Keep rows with in_post1790 == True AND birth year within 1760 ± 20 (1740..1780).
      - Drop rows with birth year outside the window.
      - Drop rows with missing/invalid birth year.
      - Add parent_id and parent_ids_all from edges.
    """
    # ---- Fake get_profile (inject via monkeypatch or function arg) ----
    def fake_get_profile(profile_key: str):
        return {
            "C_OK":      {"BirthDate": "1765-01-01"},  # within range -> keep
            "C_YOUNG":   {"BirthDate": "1790-06-01"},  # out of range -> drop
            "C_MISSING": {},                            # missing -> drop by default
        }.get(profile_key, {})

    # ---- Build edges JSON ----
    edges = [
        {"parent_id": "P-5", "child_id": "C_OK"},
        {"parent_id": "P-2", "child_id": "C_MULTI"},
        {"parent_id": "P-9", "child_id": "C_MULTI"},  # test multiple parents (won't be kept in this test)
    ]
    edges_path = tmp_path / "edges.json"
    edges_path.write_text(json.dumps(edges), encoding="utf-8")

    # ---- Build input CSV ----
    df_in = pd.DataFrame(
        [
            {"child_id": "C_OK",      "child_name": "John Smith", "state": "PA", "in_post1790": True,  "error": ""},
            {"child_id": "C_YOUNG",   "child_name": "John Smith", "state": "PA", "in_post1790": True,  "error": ""},
            {"child_id": "C_MISSING", "child_name": "Jane Smith", "state": "MA", "in_post1790": True,  "error": ""},
            {"child_id": "C_FALSE",   "child_name": "Other",      "state": "NY", "in_post1790": False, "error": ""},
        ]
    )
    in_csv = tmp_path / "matches.csv"
    df_in.to_csv(in_csv, index=False)

    out_csv = tmp_path / "filtered.csv"

    # ---- Run ----
    df_out = mod.refine_matches(
        in_csv=str(in_csv),
        edges_json=str(edges_path),
        out_csv=str(out_csv),
        center_year=1760,
        window=20,
        drop_if_missing_year=True,
        fetch_profile=fake_get_profile,   # dependency injection
    )

    # ---- Assert ----
    # Only C_OK should remain
    assert set(df_out["child_id"]) == {"C_OK"}
    # parent columns exist
    assert "parent_id" in df_out.columns
    assert "parent_ids_all" in df_out.columns
    # parent mapping correct
    row = df_out.iloc[0]
    assert row["parent_id"] == "P-5"
    assert row["parent_ids_all"] == "P-5"  # only one parent for C_OK

    # out_csv should match df_out
    check = pd.read_csv(out_csv)
    assert set(check["child_id"]) == {"C_OK"}

def test_refine_matches_drops_same_parent_child_name(tmp_path):
    """
    Rows where parent and child have the same normalized name should be dropped.
    Rows with different names should remain.
    """

    # --- Fake get_profile that returns both child and parent profiles ---
    def fake_get_profile(profile_key: str):
        # Children (by child_id)
        if profile_key == "C1":
            return {"BirthDate": "1765-01-01"}  # within 1760±20
        if profile_key == "C2":
            return {"BirthDate": "1750-02-02"}  # within 1760±20

        # Parents (by parent_id)
        if profile_key == "P1":
            # Same name as child C1 -> should cause drop
            return {"RealName": "John", "LastNameCurrent": "Smith"}
        if profile_key == "P2":
            # Different name from child C2 -> should keep
            return {"RealName": "Thomas", "LastNameCurrent": "Jones"}

        return {}

    # --- Edges: map children to parents ---
    edges = [
        {"parent_id": "P1", "child_id": "C1"},
        {"parent_id": "P2", "child_id": "C2"},
    ]
    edges_path = tmp_path / "edges.json"
    edges_path.write_text(json.dumps(edges), encoding="utf-8")

    # --- Matches CSV: both children “match” initially ---
    df_in = pd.DataFrame(
        [
            {"child_id": "C1", "child_name": "John Smith", "state": "PA", "in_post1790": True, "error": ""},
            {"child_id": "C2", "child_name": "Mary Jones", "state": "MA", "in_post1790": True, "error": ""},
        ]
    )
    in_csv = tmp_path / "task_3_matches.csv"
    df_in.to_csv(in_csv, index=False)

    out_csv = tmp_path / "filtered.csv"

    # --- Run refine_matches (inject fake_get_profile) ---
    df_out = mod.refine_matches(
        in_csv=str(in_csv),
        edges_json=str(edges_path),
        out_csv=str(out_csv),
        center_year=1760,
        window=20,
        drop_if_missing_year=True,
        fetch_profile=fake_get_profile,
    )

    # --- Assertions ---
    # C1 should be DROPPED (same name as parent), C2 should be KEPT
    assert set(df_out["child_id"]) == {"C2"}

    # Parent mapping columns should exist
    assert "parent_id" in df_out.columns
    assert "parent_ids_all" in df_out.columns

    # And parent_id for the kept row should be P2
    row = df_out.iloc[0]
    assert row["parent_id"] == "P2"