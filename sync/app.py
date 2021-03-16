from selenium.webdriver.chrome.options import Options
from selenium import webdriver

import os
from time import sleep, time
from tappa_handler import update_data

def get_chrome_options() -> None:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

def print_status(msg):
    print(msg, flush=True)

def sync_data():
    while True:
        try:
            print_status("Running sync (Started %d)" % int(time()))
            driver = webdriver.Chrome(options=get_chrome_options())

            username = os.environ["TAPPA_USERNAME"]
            password = os.environ["TAPPA_PASSWORD"]
            update_data(driver, username, password)

            driver.close()
        except Exception as e:
            print_status("Failed tappa sync due to exception: %s" % e)
            if driver is not None:
                try:
                    driver.close()
                except:
                    print_status("Could not close driver")

        print_status("Waiting 10 minutes until next sync")
        sleep(600)


if __name__ == "__main__":
    sync_data()
