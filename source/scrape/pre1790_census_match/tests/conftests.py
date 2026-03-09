import os
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture(autouse=True)
def no_env_credentials(monkeypatch):
    """
    Ensure that any code which reads ANCESTRY_USER / ANCESTRY_PASS
    from the environment sees *some* value, so that auth.py
    doesn’t blow up if those vars aren’t set on the CI server.
    By marking autouse=True, this fixture runs for every test,
    transparently applying the monkeypatch.
    """
    monkeypatch.setenv("ANCESTRY_USER", "dummy_user")
    monkeypatch.setenv("ANCESTRY_PASS", "dummy_pass")

@pytest.fixture
def dummy_html(tmp_path):
    """
    Create a small temporary HTML file on disk and return its path.
    Tests that need a simple file-backed HTML (e.g. testing file I/O
    or parser functions that read from disk) can request this fixture
    and get a valid filename without polluting the real filesystem.
    """
    p = tmp_path / "dummy.html"
    p.write_text("<html><body>hello world</body></html>")
    return str(p)