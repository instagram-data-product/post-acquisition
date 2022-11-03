from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.instagram.com/")
html = driver.page_source
file = open("instagram.html", "w")
file.write(html)
file.close()

#Accepter les cookies
cookie = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//button[contains(text(), "Autoriser les cookies essentiels et optionnels")]')))
time.sleep(2)
cookie.click()

#Se connecter 
username = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input[name="username"]')))
password = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input[name="password"]')))

username.clear()
username.send_keys("paul.machuel@esme.fr")
time.sleep(2)
password.clear()
password.send_keys("Paum18mai*")
time.sleep(2)

login = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'button[type="submit"]')))
login.click()

#Ne pas enregistrer les identifiants
not_now = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//button[contains(text(), "Plus tard")]')))
not_now.click()
time.sleep(2)

notification = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//button[contains(text(), "Plus tard")]')))
notification.click()
time.sleep(2)

#Cliquer sur le bouton recherche
click_on_search = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Recherche"]')))
click_on_search.click()

#Chercher un nom
searchbox = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Rechercher"]')))
searchbox.clear()

keyword = "lonepsi"
searchbox.send_keys(keyword)
time.sleep(5)
searchbox.send_keys(Keys.ENTER)
time.sleep(5)
searchbox.send_keys(Keys.ENTER)
time.sleep(5)

#scroll
#driver.execute_script(“window.scrollTo(0, 4000);”)

#select images

images = driver.find_element(By.TAG_NAME, 'img').get_attribute("src")
images = images[:-2] #slicing-off IG logo and Profile picture
print("Number of scraped images: ", len(images))

#download images


