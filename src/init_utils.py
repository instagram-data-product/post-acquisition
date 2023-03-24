import glob
import os
import time
import urllib.request
import re

from google.cloud import storage
from google.cloud import bigquery
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
from google.oauth2.service_account import Credentials

import random


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
    time.sleep(3)
    password.send_keys("Paumm18mai*")
    time.sleep(2)
    login = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login.click()


def save_login_info(driver):
    time.sleep(2)
    not_now = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Enregistrer les identifiants")]')))
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
    time.sleep(5)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(3)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(2)



def collect_post(driver, username):
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
        is_video = len(driver.find_elements(By.CSS_SELECTOR, "video")) > 0
        if is_video:
            continue
        is_img_valid = WebDriverWait(driver, 100).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "img[style='object-fit: cover;']")))
        if not is_img_valid:
            continue
        download_image(driver, username)
        retrieve_post_data(driver, username)


def download_image(driver, username):
    shortcode = driver.current_url.split("/")[-2]
    download_url = driver.find_element(By.CSS_SELECTOR, "img[style='object-fit: cover;']").get_attribute('src')
    folder_name = os.path.join('Images', username)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_path = os.path.join(folder_name, '{}.jpg'.format(shortcode))
    urllib.request.urlretrieve(download_url, file_path)



def retrieve_post_data(driver, username):
    try:
        caption = driver.find_element(By.CLASS_NAME, "_a9zs").text
    except NoSuchElementException:
        caption = "no captions"
    likes_list = []
    try:
        likes_num = driver.find_element(By.CLASS_NAME, "x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.xt0psk2.x1i0vuye.xvs91rp.x1s688f.x5n08af.x10wh9bi.x1wdrske.x8viiok.x18hxmgj").text
    except NoSuchElementException:
        likes_num = "0"
    print(likes_num)
    img_url = driver.current_url
    if "instagram.com/p/" in img_url:
        # Extraire l'identifiant de publication de l'URL
        id_url = img_url.split("/")[4].split("?")[0]
    gs_uri = f"gs://instagram_scrapping_bucket/posts/{username}/{id_url}.jpg"
    likes_list.append(likes_num)
    print(gs_uri)
    save_to_bigquery(likes_list, caption, username, gs_uri)


def save_to_bigquery(likes_num, caption, username, gs_uri):
    # Créez un DataFrame pandas à partir de vos listes
    df = pd.DataFrame({'likes_num': likes_num, 'caption': caption, 'username': username, 'gs_uri': gs_uri})

    # Exporter le DataFrame dans BigQuery
    from google.cloud import bigquery

    # Chargez vos informations d'identification depuis un fichier JSON
    credentials = Credentials.from_service_account_file(
        'D:/Users/Paul/Documents/inge_3/projet_insta/key_google/ServiceKey_GoogleCloud.json')

    # Instanciez un client BigQuery en utilisant vos informations d'identification
    client = bigquery.Client(credentials=credentials)

    # Définissez le nom de votre table BigQuery
    table_id = "your_dataset.Insta_Scrapping"

    # Écrivez le DataFrame dans la table BigQuery
    df.to_gbq(table_id, client.project, if_exists='append')

def export_to_gcs(local_directory_path: str, dest_bucket_name: str, dest_blob_name: str, username: str):
    storage_client = storage.Client()
    rel_paths = glob.glob(os.path.join(local_directory_path, username) + '/**', recursive=True)
    bucket = storage_client.get_bucket(dest_bucket_name)
    # bucket = GCS_CLIENT.bucket(dest_bucket_name)
    for local_file in rel_paths:
        if os.path.isfile(local_file):
            remote_path = f'{dest_blob_name}/{username}/{"/".join(local_file.split(os.sep)[2:])}'
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)


