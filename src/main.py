from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from init_utils import accept_cookies, login, save_login_info, turn_off_notifications, search_profile,  \
    export_to_gcs, collect_post, change_location
import random

LOCAL_IMAGES_FOLDER = r"Images"
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
    collect_post(driver, username)
    export_to_gcs(LOCAL_IMAGES_FOLDER, GCS_BUCKET_NAME, BLOB_NAME, username)
    # Go to a user page
    # Get all the images (handle the scrolling)


keywords_list = [
    "kendricklamar",
    "maxoucharles"
]
NordVPN_Countries = ['United States', 'Canada', 'Argentina', 'Brazil', 'Mexico', 'Costa Rica', 'Chile',
                     'United Kingdom', 'Germany', 'France', 'Netherlands', 'Sweden', 'Switzerland',
                     'Denmark', 'Poland', 'Italy', 'Spain', 'Norway', 'Belgium', 'Ireland', 'Czech Republic',
                     'Austria', 'Portugal', 'Finland', 'Ukraine', 'Romania', 'Serbia', 'Hungary', 'Luxembourg',
                     'Slovakia', 'Bulgaria', 'Latvia', 'Greece', 'Iceland', 'Estonia', 'Albania', 'Croatia',
                     'Cyprus', 'Slovenia', 'Moldova', 'Bosnia and Herzegovina', 'Georgia', 'North Macedonia',
                     'Turkey', 'South Africa', 'India', 'Israel', 'Turkey', 'United Arab Emirates', 'Australia',
                     'Taiwan', 'Singapore', 'Japan', 'Hong Kong', 'New Zealand', 'Malaysia', 'Vietnam', 'Indonesia',
                     'South Korea', 'Thailand']
i=0
for keywords in keywords_list:
    i += 1
    print("Data Acquisition for " + keywords)
    get_html_from_profile_url(keywords)
    if i == 10:
        change_location(random.choice(NordVPN_Countries))
        i=0



