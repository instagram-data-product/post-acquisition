from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from init_utils import accept_cookies, login, save_login_info, turn_off_notifications, search_profile,  \
    scrolling_profile, find_and_collect_posts, export_to_gcs

LOCAL_IMAGES_FOLDER = "Images"
GCS_BUCKET_NAME = "instagram_scrapping_bucket"
BLOB_NAME = "posts"


def get_html_from_profile_url(username):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.instagram.com/")

    accept_cookies(driver)
    login(driver)
    save_login_info(driver)
    turn_off_notifications(driver)
    search_profile(driver, username)
    scrolling_profile(driver)
    find_and_collect_posts(driver)
    export_to_gcs(LOCAL_IMAGES_FOLDER, GCS_BUCKET_NAME, BLOB_NAME, username)
    # Go to a user page
    # Get all the images (handle the scrolling)


keywords_list = [
    "natsuleshiba",
    "fabwildpix",
    "rogerfederer"
]

for keywords in keywords_list:
    print("Data Acquisition for " + keywords)
    get_html_from_profile_url(keywords)

