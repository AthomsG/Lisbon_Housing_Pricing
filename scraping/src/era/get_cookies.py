from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

options = Options()
options.add_experimental_option("detach", True)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get('https://www.era.pt/comprar')

# wait for the page to load
time.sleep(5)

cookies = driver.get_cookies()
cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

requestverificationtoken = driver.execute_script(
    "return document.querySelector('input[name=__RequestVerificationToken]').value"
)

with open('cookies.json', 'w') as f:
    json.dump({'cookies': cookie_dict, 'requestverificationtoken': requestverificationtoken}, f)

driver.quit()

print("Cookies and request verification token have been saved.")