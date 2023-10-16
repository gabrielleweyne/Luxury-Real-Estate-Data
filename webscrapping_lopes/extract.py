import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup # Parseador de HTML

def get_html_soup(url, xpath):
    print('Starting up driver...')
    options = webdriver.FirefoxOptions() # Opções do webdrive
    options.add_argument("-headless") # Rodar o firefox no terminal

    print('Opening url...')
    driver = webdriver.Firefox(options=options) # Por default ele já procura onde o Firefox instalou e onde está o geckodriver
    driver.get(url) # Bater na página

    print('Waiting load...')
    time.sleep(4) # esperar 5 segundos para a página carregar

    print('Getting HTML...')
    el = driver.find_element(By.XPATH, xpath)
    html_ctnt = el.get_attribute('outerHTML')

    driver.quit() # fechar o navegador

    print('Returning Soup')
    return BeautifulSoup(html_ctnt, 'lxml')
    