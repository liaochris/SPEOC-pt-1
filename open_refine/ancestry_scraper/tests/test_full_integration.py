import csv
import sys
import pytest
import importlib

@pytest.mark.integration
def test_process_name_writes_real_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    state = "DE"
    # 1) Pick a real path for our output files
    results_file    = tmp_path / f"results_{state}.csv"
    checkpoint_file = tmp_path / f"progress_{state}.json"

    # 2) Override the config module's variables directly
    import ancestry_scraper.config as cfg
    #monkeypatch.setattr(cfg, "OUTPUT_CSV",   str(results_file))
    #monkeypatch.setattr(cfg, "CHECKPOINT_FILE", str(checkpoint_file))

    # 3) Clear any previous imports so reload sees the new config
    for mod in (
        "ancestry_scraper.storage",
        "ancestry_scraper.worker",
    ):sys.modules.pop(mod, None)

    # 4) Reload in dependency order
    import ancestry_scraper.storage as storage
    importlib.reload(storage)

    monkeypatch.setattr(
        storage,
        "_results_path",
        lambda state: tmp_path / f"results_{state}.csv",
    )
    monkeypatch.setattr(
        storage,
        "_progress_path",
        lambda state: tmp_path / f"progress_{state}.json",
    )

    import ancestry_scraper.worker as worker
    importlib.reload(worker)

    # 5) Now import the functions under test
    from ancestry_scraper.storage import load_progress
    from ancestry_scraper.worker import process_name

    # 6) Sanity‐check: make sure files don’t already exist
    if results_file.exists():    
        results_file.unlink()
    if checkpoint_file.exists(): 
        checkpoint_file.unlink()

    # 7) Run your scraper over three real names
    for name in ("Thomas McKean", "Alexander McBeath", "John Passmore"):
        process_name(name, state, event_year=1777, event_x=10)

    # 8) Progress file should mark each “done”
    prog = load_progress(state)
    for nm in ("Thomas McKean", "Alexander McBeath", "John Passmore"):
        assert prog.get(nm) == "done", f"{nm} should be marked done"

    # 9) There really should now be a results.csv on disk
    assert results_file.exists(), "Expected a real results.csv to be created"

    # 10) Read it and verify header + 3 lines
    with results_file.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["name", "url", "county"]
    assert len(rows) == 1 + 3  # header + 3 data rows

    # 11) Check each URL and county
    for name, url, county in rows[1:]:
        fmt = name.replace(" ", "_")
        assert f"name={fmt}" in url
        assert "&event=1777"      in url
        assert "&event_x=10-0-0"  in url
        assert county == "New Castle"