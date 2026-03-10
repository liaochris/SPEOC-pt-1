from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from source.lib.selenium_base import GetChromeDriver

def GetAuthenticatedDriver():
    driver = GetChromeDriver(headless=False)

    # TODO: update entry point URL in future step
    driver.get("https://www.galileo.usg.edu/express?link=zual&inst=git1")

    # wait up to 5 minutes for the redirect into ancestrylibrary.com
    WebDriverWait(driver, 300).until(
        EC.url_contains("ancestrylibrary.com")
    )

    return driver
