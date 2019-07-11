import chromedriver_binary
import redis
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from credential import Credential
from webdriver_wrapper import WebdriverWrapper


class Rakumachi:
    def __init__(self, store, debug=False):
        self.debug = debug
        self._credentials = None
        self._datastore = store

    def with_credential(self, user, password):
        self._credentials = Credential(user, password)
        return self

    def search(self, **queries):
        with WebDriverWrapper(self.debug) as driver:
            if self._credentials is not None:
                Rakumachi.login(driver, self._credentials)
            driver.get(Rakumachi.build_search_url(queries))
            while True:
                for house in driver.find_element_by_class_name("propertyBlock"):
                    Rakumachi.move_to_detail(driver, house)
                    try:
                        try:
                            company_link = driver.find_element_by_css_selector(".realtor___detailLink a")
                        except:
                            continue  # company link not found
                        self.register_company_info(driver, company_link)
                    finally:
                        Rakumachi.back_to_origin(driver)
                if not Rakumachi.move_to_next(driver):
                    break

    @staticmethod
    def login(driver, credential):
        driver.get("https://www.rakumachi.jp/my/")
        driver.find_element_by_id("login_e_mail").send_keys(credential.user)
        driver.find_element_by_id("login_password").send_keys(credential.password)
        driver.find_element_by_css_selector('input[type="submit"]').click()

    @staticmethod
    def build_search_url(queries):
        queryparams = []
        if "area" in queries and isinstance(queries["area"], list):
            queryparams.extend(list(map(lambda a: "area[]=" + a, queries["area"])))
        paramstr = "" if len(queryparams) == 0 else "?" + "&".join(queryparams)
        return "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/" + paramstr

    @staticmethod
    def move_to_next(driver):
        next_link = driver.find_elements_by_css_selector("#pagination_next_bottom")
        if len(next_link) == 0:
            return False
        next_link[0].click()
        return True

    @staticmethod
    def move_to_detail(driver, house):
        blocks = house.find_element_by_class_name("propertyBlock__mainArea")
        if len(blocks) > 0:
            ActionChains(driver).key_down(Keys.CONTROL).click(blocks[0]).perform()
            driver.switch_to.window(driver.window_handles[-1])

    @staticmethod
    def back_to_origin(driver):
        driver.execute_script("window.close()")
        driver.switch_to.window(driver.window_handles[0])

    def register_company_info(self, driver, company_link):
        company_name = company_link.text
        url = company_link.get_attribute("href")
        hash = url.replace("https://www.rakumachi.jp/property/realtor/", "")
        if self._datastore.exists(hash):
            return
        driver.get(url)
        table_elements = driver.find_elements_by_css_selector(".outlinetable tr th,.outlinetable tr td")
        company_data = list(map(lambda x: x.text, table_elements))
        self._datastore.register_company(hash, company_name, company_data)


# def search(debug):
#     global _driver
#     if (_driver is None):
#         _init_driver(debug)
#
#     try:
#         rds = redis.Redis()
#         login("mt.village12@gmail.com", "jAGYLqGMBo")
#
#         # search tokyo
#         _search({"area": [13]})
#
#         while(True):
#             house_list = driver.find_elements_by_css_selector(".propertyBlock .propertyBlock__mainArea")
#             next_link = driver.find_elements_by_css_selector("#pagination_next_bottom")
#             for house in house_list:
#                 ActionChains(driver).key_down(Keys.CONTROL).click(house).perform()
#                 driver.switch_to.window(driver.window_handles[-1])
#                 house_url = driver.current_url
#                 try:
#                     try:
#                         detail_link = driver.find_element_by_css_selector(".realtor___detailLink a")
#                         company_name = detail_link.text
#                         company_url = detail_link.get_attribute("href")
#                         company_hash = company_url.replace("https://www.rakumachi.jp/property/realtor/", "")
#                     except:
#                         yield { "company": None, "hash": None }
#                         continue
#                     try:
#                         if rds.exists(company_hash) > 0:
#                             continue
#                         driver.get(company_url)
#                         table_elements = driver.find_elements_by_css_selector(".outlinetable tr th,.outlinetable tr td")
#                         rds.hset(company_hash, "name", company_name)
#                         rds.hset(company_hash, "data", "\t".join(list(map(lambda x: x.text, table_elements))))
#                     except:
#                         yield { "company": company_name, "hash": company_hash }
#                 finally:
#                     driver.execute_script("window.close()")
#                     driver.switch_to.window(driver.window_handles[0])
#             if len(next_link) == 0:
#                 break
#             next_link[0].click()
#     finally:
#         driver.quit()
