import pytest
import source.lib.ancestry_scraper.worker as worker
from source.lib.ancestry_scraper.scraper import MatchResult

class DummyStorage:
    def __init__(self):
        self.rows = []
        self.prog = {}
    def LoadProgress(self, state):
        return self.prog
    def SaveProgress(self, p, state):
        self.prog = p
    def AppendResult(self, row, state):
        self.rows.append(row)

@pytest.fixture(autouse=True)
def patch_storage(monkeypatch):
    ds = DummyStorage()
    monkeypatch.setattr(worker, "LoadProgress",  ds.LoadProgress)
    monkeypatch.setattr(worker, "SaveProgress",  ds.SaveProgress)
    monkeypatch.setattr(worker, "AppendResult",  ds.AppendResult)
    return ds

def test_process_name_success(monkeypatch, patch_storage):
    monkeypatch.setattr(worker, "ScrapeLoanOffice",
                        lambda name, state, event_year: MatchResult(["TestCo"], "Complete Match", "URL1", "1_1", 0))

    worker.ProcessName("Alice", "DE", event_year=1777)

    assert patch_storage.rows == [["Alice", 1777, "1_1", 0, "URL1", "Complete Match", "TestCo"]]
    assert patch_storage.prog["Alice"] == "done"

def test_process_name_error(monkeypatch, patch_storage):
    monkeypatch.setattr(
            worker,
            "ScrapeLoanOffice",
            lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
        )
    worker.ProcessName("Bob", "DE")
    assert "error: fail" in patch_storage.prog["Bob"]
