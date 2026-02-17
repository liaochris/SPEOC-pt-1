import json
import requests, random, time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import RATE_LIMIT_SECONDS, MAX_RETRIES, USER_AGENTS

def get_session():
    s = requests.Session() # create a new session
    retries = Retry(
        total=MAX_RETRIES, # max retries
        backoff_factor=1, # delays of 1s, 2s, 4s between retries
        status_forcelist=[500,502,503,504] # error codes which trigger a retry
    )
    s.mount("https://", HTTPAdapter(max_retries=retries)) # create an HTTPAdapter with our retry rules
    s.headers.update({"User-Agent": random.choice(USER_AGENTS)}) # create rotating user agends to avoid bot detection
    return s

def rate_limited(func): # avoid rate-limits
    # a decorator to enforce a pause between each call of func 
    def wrapper(*args, **kwargs): 
        time.sleep(RATE_LIMIT_SECONDS)
        return func(*args, **kwargs)
    return wrapper

def get_library_session():
    """
    Create a requests.Session pre-loaded with the AncestryLibrary cookies
    you exported manually. This bypasses Selenium entirely.
    """
    s = requests.Session()
    # load your exported cookies
    for cookie in json.load(open("ancestry_cookies.json", "r")):
        # adjust domain if the cookie JSON uses ".ancestrylibrary.com"
        s.cookies.set(
            name=cookie['name'],
            value=cookie['value'],
            domain=cookie.get('domain'),
            path=cookie.get('path', '/')
        )
    return s