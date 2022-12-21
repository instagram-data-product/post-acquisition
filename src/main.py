from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from init_utils import accept_cookies, login, save_login_info, turn_off_notifications, search_profile, select_images_profile, download_images


def export_html(driver):
    html = driver.page_source
    file = open("instagram.html", "w", encoding="utf-8")
    file.write(html)
    file.close()


def get_html_from_profile_url():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.instagram.com/")


    accept_cookies(driver)
    login(driver)
    save_login_info(driver)
    turn_off_notifications(driver)
    search_profile(driver)
    select_images_profile(driver)
    download_images(driver)
    export_html(driver)

    # Go to a user page
    # Get all the images (handle the scrolling)


get_html_from_profile_url()
