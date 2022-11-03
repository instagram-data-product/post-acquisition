from selenium import webdriver 
from instascrape import Profile, scrape_posts

driver_path = "C:/Users/paulm/Documents/inge_3/chromedriver/chromedriver.exe"
driver = webdriver.Chrome(executable_path=driver_path)


SESSIONID = "1w8HWfZzkLUvI2KxM4hVATVHTQ1j0EM2"
headers = {"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57",
           "cookie": f"sessionid={SESSIONID};"}


Paul = Profile("kanyewest")
Paul.scrape(headers=headers)

posts = Paul.get_posts(webdriver=webdriver, login_first=True)
scraped, unscraped = scrape_posts(posts, headers=headers, pause=10, silent=False)
