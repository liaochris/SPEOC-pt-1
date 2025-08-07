import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_authenticated_driver():
    opts = Options()
    # remove headless so you can see it (optional)
    # opts.add_argument("--headless")

    # Point to your real Chrome user data dir:
    #   on macOS it's usually "~/Library/Application Support/Google/Chrome"
    #   on Windows "%LOCALAPPDATA%\\Google\\Chrome\\User Data"
    opts.add_argument("--user-data-dir=/Users/davidcho/Library/Application Support/Google/Chrome/TestProfile")

    driver = webdriver.Chrome(options=opts)

    # 1) hit your school’s proxy landing page
    driver.get("https://www.galileo.usg.edu/express?link=zual&inst=git1")

    # 2) wait up to 5 minutes for the redirect into ancestrylibrary.com
    WebDriverWait(driver, 300).until(
        EC.url_contains("ancestrylibrary.com")
    )


    """
    # 1) Kick off the login flow explicitly:
    proxy_login = "https://ancestrylibrary.proquest.com/aleweb/ale/do/login"
    driver.get(proxy_login)

    # 2) Wait a moment for the page & form to load
    time.sleep(2)

    # 3) If you’re already logged in, the next navigate should skip the login.
    #    Otherwise, this is where *you* click through the SSO screens:
    input(
      "🚦  Please complete your school’s proxy login in the opened Chrome window, "
      "then press ENTER here to continue…"
    )

    # 4) At this point, cookies should be written out to TestProfile.
    #    Give Chrome a brief moment to flush them:
    time.sleep(1)
    """

    # you should start already authenticated to your school’s proxy
    return driver