import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from difflib import SequenceMatcher
from functools import reduce

url = "https://buscacepinter.correios.com.br/app/endereco/index.php"

def str_similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def most_likely_cep(cep_a, cep_b):
    return cep_a if cep_a[0] >= cep_b[0] else cep_b

def find_cep(addr):
    print("Starting up driver...")
    options = webdriver.FirefoxOptions()  # Opções do webdrive
    options.add_argument("-headless")  # Rodar o firefox no terminal

    print(f"Opening url ({url})...")
    driver = webdriver.Firefox(
        options=options
    )  # Por default ele já procura onde o Firefox instalou e onde está o geckodriver
    driver.get(url)  # Bater na página

    print("Waiting load...")
    time.sleep(2)  # esperar 2 segundos para a página carregar

    print("Writing address...")
    driver.find_element(By.ID, "endereco").send_keys(addr)

    print("Searching...")
    driver.find_element(By.ID, "btn_pesquisar").click()
    time.sleep(2)  # esperar 2 segundos para a página carregar
    
    print("Finding CEPs")
    el = driver.find_element(By.ID, "resultado-DNEC")
    html_ctnt = el.get_attribute("outerHTML")
    cep_table = pd.read_html(html_ctnt, match="Logradouro/Nome")[0]
    cep_itr = cep_table[cep_table['Localidade/UF'].str.startswith('São Paulo/SP')].iterrows()

    print("Extrating most simmilar")
    best_cep = reduce(most_likely_cep, map(lambda tr: ((str_similar(tr[1]["Logradouro/Nome"], addr), tr[1]["CEP"])), cep_itr))

    driver.quit()  # fechar o navegador

    print(f"Most likely match for {addr} is {best_cep[1]}! ({best_cep[0]})")
    return best_cep[1]