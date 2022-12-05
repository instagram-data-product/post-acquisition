import time

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def download(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(3)

    html = driver.page_source
    file = open("instagram.html", "w")
    file.write(html)
    file.close()

    SCROLL_PAUSE_TIME = 1
    images_unique = []
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            driver.execute_script("window.scrollTo(document.body.scrollHeight,0);")
            break
        # This means that there is still photos to scrap
        last_height = new_height
        time.sleep(1)
        # Retrive the html
        html_to_parse = str(driver.page_source)
        html = bs(html_to_parse, "html5lib")
        # Get the image's url
        images_url = html.findAll("img", {"class": "FFVAD"})

        # Check if they are unique
        in_first = set(images_unique)
        in_second = set(images_url)

        in_second_but_not_in_first = in_second - in_first

        result = images_unique + list(in_second_but_not_in_first)
        images_unique = result
    # Close the webdriver
    driver.close()

    for i in range(len(images_unique)):
        # Save each image.jpg file
        name = "image" + str(i) + ".jpg"
        with open(name, 'wb', encoding="utf-8") as handler:
            img_data = requests.get(images_unique[i].get("src")).content
            handler.write(img_data)

    return


download("https://www.instagram.com/lonepsi")
