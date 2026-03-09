import csv
import sys
import pytest
import importlib

@pytest.mark.integration
def test_process_name_writes_real_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    state = "NY"
    results_file    = tmp_path / f"results_{state}.csv"
    checkpoint_file = tmp_path / f"progress_{state}.json"

    import source.lib.ancestry_scraper.config as cfg

    for mod in (
        "source.lib.ancestry_scraper.storage",
        "source.lib.ancestry_scraper.worker",
    ):
        sys.modules.pop(mod, None)

    import source.lib.ancestry_scraper.storage as storage
    importlib.reload(storage)

    monkeypatch.setattr(
        storage,
        "_ResultsPath",
        lambda state: tmp_path / f"results_{state}.csv",
    )
    monkeypatch.setattr(
        storage,
        "_ProgressPath",
        lambda state: tmp_path / f"progress_{state}.json",
    )

    import source.lib.ancestry_scraper.worker as worker
    importlib.reload(worker)

    from source.lib.ancestry_scraper.storage import LoadProgress
    from source.lib.ancestry_scraper.worker import ProcessName

    if results_file.exists():
        results_file.unlink()
    if checkpoint_file.exists():
        checkpoint_file.unlink()

    for name in ("Thomas McKean", "Alexander McBeath", "John Passmore"):
        ProcessName(name, state, event_year=1777, event_x=10)

    prog = LoadProgress(state)
    for nm in ("Thomas McKean", "Alexander McBeath", "John Passmore"):
        assert prog.get(nm) == "done", f"{nm} should be marked done"

    assert results_file.exists(), "Expected a real results.csv to be created"

    with results_file.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["name", "url", "county"]
    assert len(rows) == 1 + 3

    for name, url, county in rows[1:]:
        fmt = name.replace(" ", "_")
        assert f"name={fmt}" in url
        assert "&event=1777"      in url
        assert "&event_x=10-0-0"  in url
