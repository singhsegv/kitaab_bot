import time
import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

def download_book(url, name):
    chromedriver = '/home/rajdeep1008/Desktop/chromedriver'
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    driver.get(url)
    link = driver.find_element_by_link_text(name)
    actionChains = ActionChains(driver)
    actionChains.context_click(link)
    actionChains.send_keys(Keys.ARROW_DOWN)
    actionChains.send_keys(Keys.ARROW_DOWN)
    actionChains.send_keys(Keys.ARROW_DOWN)
    actionChains.send_keys(Keys.ARROW_DOWN)
    actionChains.send_keys(Keys.RETURN)
    actionChains.perform()

    while True:
        if not os.path.isfile('/home/rajdeep1008/Downloads/' + name + '.pdf'):
            time.sleep(5)
        else:
            break
    driver.quit()

# download_book('http://it-ebooks.info/book/6719/', 'Android Studio Game Development')
