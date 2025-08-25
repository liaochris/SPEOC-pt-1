import time
import pytest
from ancestry_scraper.session import get_session, rate_limited

def test_get_session_headers_and_retries():
    s = get_session()
    # Must have a User-Agent (what kind of client?) header -- make it appear as a normal browser
    ua = s.headers.get("User-Agent", "")
    assert "Mozilla" in ua

    # Test that retry adapter is mounted
    assert "https://" in s.adapters

def test_rate_limited_decorator(monkeypatch):
    calls = []
    def fake_sleep(sec):
        calls.append(sec)
    # replace time.sleep with our fake_skeep function allows us to test if it paused correctly
    monkeypatch.setattr(time, "sleep", fake_sleep) 
    
    @rate_limited
    def f(x):
        return x * 2

    result = f(3)
    assert result == 6
    # ensure it slept once with the configured interval
    from ancestry_scraper.config import RATE_LIMIT_SECONDS
    assert calls == [RATE_LIMIT_SECONDS]