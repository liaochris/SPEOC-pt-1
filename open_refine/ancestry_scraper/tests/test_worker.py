import pytest
from ancestry_scraper.worker import process_name

# mimic our storage.py
class DummyStorage:
    def __init__(self):
        self.rows = [] # collect any rows from append_result
        self.prog = {}
    def load_progress(self):
        return self.prog # returns our internal dict
    def save_progress(self, p):
        self.prog = p # replaces it
    def append_result(self, row):
        self.rows.append(row) # captures results which would usually go to results.csv

# overwrrite the methods with our dummy storage methods
@pytest.fixture(autouse=True)
def patch_storage(monkeypatch):
    ds = DummyStorage()
    monkeypatch.setattr("worker.load_progress", ds.load_progress)
    monkeypatch.setattr("worker.save_progress", ds.save_progress)
    monkeypatch.setattr("worker.append_result", ds.append_result)
    return ds

def test_process_name_success(monkeypatch, patch_storage):
    # stub search + parse
    monkeypatch.setattr("worker.fetch_search_page", lambda n,**k: ("<html>ok</html>", "URL1"))
    monkeypatch.setattr("worker.parse_residence_county", lambda html: "TestCo")
    process_name("Alice", event_year=1777)
    # should have recorded one row
    assert patch_storage.rows == [["Alice", "URL1", "TestCo"]] # storage should only contain one row
    assert patch_storage.prog["Alice"] == "done" # alice should be processed

# test error handling
def test_process_name_error(monkeypatch, patch_storage):
    monkeypatch.setattr("worker.fetch_search_page", lambda *a,**k: (_ for _ in ()).throw(Exception("fail")))
    process_name("Bob")
    assert "error: fail" in patch_storage.prog["Bob"] # bob should be marked with an error