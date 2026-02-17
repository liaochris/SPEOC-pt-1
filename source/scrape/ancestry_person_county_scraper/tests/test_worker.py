import pytest
import ancestry_scraper.worker as worker

# mimic our storage.py
class DummyStorage:
    def __init__(self):
        self.rows = [] # collect any rows from append_result
        self.prog = {}
    def load_progress(self, state):
        return self.prog # returns our internal dict
    def save_progress(self, p, state):
        self.prog = p # replaces it
    def append_result(self, row, state):
        self.rows.append(row) # captures results which would usually go to results.csv

# overwrrite the methods with our dummy storage methods
@pytest.fixture(autouse=True)
def patch_storage(monkeypatch):
    ds = DummyStorage()
    monkeypatch.setattr(worker, "load_progress",    ds.load_progress)
    monkeypatch.setattr(worker, "save_progress",    ds.save_progress)
    monkeypatch.setattr(worker, "append_result",    ds.append_result)
    return ds

def test_process_name_success(monkeypatch, patch_storage):
    # also patch fetch + parse on the worker module
    monkeypatch.setattr(worker, "fetch_search_page",
                        lambda name, state, **kw: ("<html/>", "URL1"))
    monkeypatch.setattr(worker, "parse_residence_county",
                        lambda html: "TestCo")

    worker.process_name("Alice", "DE", event_year=1777, event_x=10)

    assert patch_storage.rows == [["Alice", "URL1", "TestCo"]] # storage should only contain one row
    assert patch_storage.prog["Alice"] == "done" # alice should be processed

# test error handling
def test_process_name_error(monkeypatch, patch_storage):
    monkeypatch.setattr(
            worker,
            "fetch_search_page",
            lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
        )    
    worker.process_name("Bob", "DE")
    assert "error: fail" in patch_storage.prog["Bob"] # bob should be marked with an error