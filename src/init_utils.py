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


def select_images_profile(driver):
    # scroll
    driver.execute_script("window.scrollTo(0, 800);")
    # select images
    new_images = []
    images = driver.find_elements(By.TAG_NAME, "img")
    images = [new_images.append(image.get_attribute("src")) for image in images]
    # new_images.remove('data:image/png;base64,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')
    new_images = new_images[:-2]
    # print("Number of scraped images: ", len(images))
    # print(new_images)

    image_id = 0
    for url in new_images:
        image_id = image_id + 1
        img_path = "Images"
        if not os.path.exists(img_path):
            os.makedirs(img_path)
            urllib.request.urlretrieve(url, "images/img_{}.jpg".format(image_id))


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


def find_and_collect_posts(driver):
    post_urls = []
    links = driver.find_elements(By.TAG_NAME, "a")  # Make sure to get all the links
    for link in links:
        post = link.get_attribute('href')
        if '/p/' in post:
            post_urls.append(post)

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
    caption = driver.find_element(By.CLASS_NAME, "_a9zs").text
    print(caption)
    caption_list.append(caption)
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
