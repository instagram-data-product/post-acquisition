import glob
import os
import time
import urllib.request

from google.cloud import storage
from google.cloud import bigquery
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def accept_cookies(driver):
    cookie = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//button[contains(text(), "Autoriser les cookies essentiels et optionnels")]')))
    time.sleep(1)
    cookie.click()


def login(driver):
    username = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
    password = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    username.clear()
    password.clear()
    username.send_keys("paul.machuel@esme.fr")
    password.send_keys("Paum18mai*")
    login = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login.click()


def save_login_info(driver):
    time.sleep(2)
    not_now = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Plus tard")]')))
    not_now.click()


def turn_off_notifications(driver):
    time.sleep(2)
    not_now = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Plus tard")]')))
    not_now.click()


def search_profile(driver, username):
    click_on_search = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Recherche"]')))
    click_on_search.click()
    searchbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Rechercher"]')))
    searchbox.clear()

    searchbox.send_keys(username)
    time.sleep(3)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(3)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(2)

def scrolling_profile(driver):
    scrolldown = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
    match = False
    while (match == False):
        last_count = scrolldown
        time.sleep(3)
        scrolldown = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
        if last_count == scrolldown:
            match = True

def collect_post(driver):
    # Initialize a list to store the post URLs
    post_urls = []
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Initialize variables to track scrolling progress
    match = False
    previous_height = driver.execute_script("return document.body.scrollHeight")
    # Keep scrolling until all images have been loaded
    while not match:
        # Wait for images to load
        time.sleep(3)
        # Find all links on the page
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            post = link.get_attribute('href')
            if '/p/' in post and post not in post_urls:
                post_urls.append(post)

        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Check if the height of the page has changed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == previous_height:
            match = True
        else:
            previous_height = new_height

    print(post_urls)

    for post in post_urls:
        driver.get(post)
        time.sleep(2)
        is_img_valid = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "img[style='object-fit: cover;']"))) is not None
        if is_img_valid:
            download_image(driver)
        retrieve_post_data(driver)
        #save_to_bigquery()

def download_image(driver):
    shortcode = driver.current_url.split("/")[-2]
    download_url = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "img[style='object-fit: cover;']"))).get_attribute('src')
    urllib.request.urlretrieve(download_url, 'images/{}.jpg'.format(shortcode))

def retrieve_post_data(driver):
    caption_list = []
    try:
        caption = driver.find_element(By.CLASS_NAME, "_a9zs").text
    except NoSuchElementException:
        caption = "no captions"
    print(caption)
    #caption_list.append(caption)
    try:
        likes_num = driver.find_element(By.CLASS_NAME, "_aacl._aaco._aacw._aacx._aada._aade").text
    except NoSuchElementException:
        likes_num = "0"
    print(likes_num)
    #save_to_bigquery(likes_num, caption)


def save_to_bigquery(likes_num, caption):
    client = bigquery.Client()

    # Prepare the data
    data = [(likes_num, caption)]

    # Get the existing table
    dataset_id = "instagram-scrapping-372812"
    table_id = f"{dataset_id}.posts"
    table = client.get_table(table_id)

    # Insert data into the table
    errors = client.insert_rows(table, data)

    # Print the errors if any
    if errors == []:
        print("Data sent successfully to BigQuery")
    else:
        print(errors)



def export_to_gcs(local_directory_path: str, dest_bucket_name: str, dest_blob_name: str, username: str):
    storage_client = storage.Client()
    rel_paths = glob.glob(local_directory_path + '/**', recursive=True)
    bucket = storage_client.get_bucket(dest_bucket_name)
    # bucket = GCS_CLIENT.bucket(dest_bucket_name)
    for local_file in rel_paths:
        remote_path = f'{dest_blob_name}/{username}/{"/".join(local_file.split(os.sep)[1:])}'
        if os.path.isfile(local_file):
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)
