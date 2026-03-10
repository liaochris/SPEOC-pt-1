import json
import requests, random, time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import RATE_LIMIT_SECONDS, MAX_RETRIES, USER_AGENTS

def GetSession():
    s = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[500,502,503,504]
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    return s

def RateLimited(func):
    def wrapper(*args, **kwargs):
        time.sleep(RATE_LIMIT_SECONDS)
        return func(*args, **kwargs)
    return wrapper

def GetLibrarySession():
    """
    Create a requests.Session pre-loaded with the AncestryLibrary cookies
    you exported manually. This bypasses Selenium entirely.
    """
    s = requests.Session()
    for cookie in json.load(open("ancestry_cookies.json", "r")):
        s.cookies.set(
            name=cookie['name'],
            value=cookie['value'],
            domain=cookie.get('domain'),
            path=cookie.get('path', '/')
        )
    return s
