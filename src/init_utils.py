from selenium.webdriver.common.by import By
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import os
import wget


def accept_cookies(driver):
    cookie = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//button[contains(text(), "Autoriser les cookies essentiels et optionnels")]')))
    time.sleep(2)
    cookie.click()


def login(driver):
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    username.clear()
    password.clear()
    username.send_keys("paul.machuel@esme.fr")
    password.send_keys("Paum18mai*")
    login = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login.click()


def save_login_info(driver):
    time.sleep(5)
    not_now = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Plus tard")]')))
    not_now.click()


def turn_off_notifications(driver):
    time.sleep(5)
    not_now = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Plus tard")]')))
    not_now.click()


def search_profile(driver):
    click_on_search = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Recherche"]')))
    click_on_search.click()
    searchbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Rechercher"]')))
    searchbox.clear()

    keyword = "lonepsi"
    searchbox.send_keys(keyword)
    time.sleep(5)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(5)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(5)


def select_images_profile(driver):
    # scroll
    driver.execute_script("window.scrollTo(0, 800);")
    # select images
    images = driver.find_elements(By.TAG_NAME, "img")
    images = [image.get_attribute("src") for image in images]
    images = images[:-2]  # slicing-off IG logo and Profile picture
    print("Number of scraped images: ", len(images))

    # Create a new directory
    name_file = "images"
    path = os.getcwd()
    path = os.path.join(path, name_file)
    os.mkdir(path)
    print(path)

    # Download images | A RETRAVAILLER
    #counter = 0
    #for image in images:
    #    save_as = os.path.join(path, name_file + str(counter) + '.jpg')
    #    wget.download(image, save_as+f'/')
    #    counter += 1
