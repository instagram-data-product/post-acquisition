from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from init_utils import accept_cookies, login, save_login_info, turn_off_notifications, search_profile


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
    print("ok1")
    turn_off_notifications(driver)
    print("ok2")
    search_profile(driver)
    print("ok3")
    export_html(driver)
    print("ok4")

    # Go to a user page
    # Get all the images (handle the scrolling)


get_html_from_profile_url()
