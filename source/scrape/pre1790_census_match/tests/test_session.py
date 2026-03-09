import time
import pytest
from source.lib.ancestry_scraper.session import GetSession, RateLimited

def test_get_session_headers_and_retries():
    s = GetSession()
    ua = s.headers.get("User-Agent", "")
    assert "Mozilla" in ua

    assert "https://" in s.adapters

def test_rate_limited_decorator(monkeypatch):
    calls = []
    def fake_sleep(sec):
        calls.append(sec)
    monkeypatch.setattr(time, "sleep", fake_sleep)

    @RateLimited
    def f(x):
        return x * 2

    result = f(3)
    assert result == 6
    from source.lib.ancestry_scraper.config import RATE_LIMIT_SECONDS
    assert calls == [RATE_LIMIT_SECONDS]
