from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import random

from init_utils import accept_cookies, login, save_login_info, turn_off_notifications, search_profile,  \
    export_to_gcs, collect_post

LOCAL_IMAGES_FOLDER = r"Images"
GCS_BUCKET_NAME = "instagram_scrapping_bucket"
BLOB_NAME = "posts"

def get_html_from_profile_url(username):
    # Obtenir une adresse IP de proxy aléatoire
    proxy_address = "89.46.99.42"

    # Configurer le proxy dans Selenium
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = proxy_address
    proxy.ssl_proxy = proxy_address
    capabilities = DesiredCapabilities.CHROME.copy()
    proxy.add_to_capabilities(capabilities)

    # Configurer le proxy dans les options de Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server={}'.format(proxy_address))

    # Lancer le navigateur avec le proxy configuré
    driver = webdriver.Chrome(options=options, desired_capabilities=capabilities, service=Service(ChromeDriverManager().install()))
    driver.get("https://www.instagram.com/")

    accept_cookies(driver)
    login(driver)
    save_login_info(driver)
    turn_off_notifications(driver)
    search_profile(driver, username)
    collect_post(driver, username)
    export_to_gcs(LOCAL_IMAGES_FOLDER, GCS_BUCKET_NAME, BLOB_NAME, username)
    # Go to a user page
    # Get all the images (handle the scrolling)


keywords_list = [
    "kendricklamar"
]

for keywords in keywords_list:
    print("Data Acquisition for " + keywords)
    get_html_from_profile_url(keywords)

