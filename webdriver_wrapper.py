import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebdriverWrapper:
    def __init__(self, debug=False):
        self._args = ["--incognito"] if debug else ["--incognito", "--headless", "--disable-gpu"]
        self._driver = None

    def __enter__(self):
        x = Options()
        for o in self._args:
            x.add_argument(o)
        self._driver = webdriver.Chrome(options=x)
        return self._driver

    def __exit__(self, ex_type, ex_value, trace):
        self._driver.quit()
        self._driver = None
