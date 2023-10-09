import time
import pandas as pd # manipulação de dados
from bs4 import BeautifulSoup # Parseador de HTML
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.FirefoxOptions() # Opções do webdrive
options.add_argument("-headless") # Rodar o firefox no terminal

driver = webdriver.Firefox(options=options) # Por default ele já procura onde o Firefox instalou e onde está o geckodriver
driver.get("https://www.lopes.com.br/busca/venda/br/sp/sao-paulo?preco-menor=15000000&placeId=ChIJ0WGkg4FEzpQRrlsz_whLqZs&origem=search") # Bater na página

time.sleep(5) # esperar 5 segundos para a página carregar

xpath = '/html/body/lps-root/lps-search/div/div/div/div/lps-search-grid/lps-search-content/div/div[1]/div[2]/lps-card-grid/div[1]/ul'
el = driver.find_element(By.XPATH, xpath)
html_ctnt = el.get_attribute('outerHTML')

driver.quit() # fechar o navegador

soup = BeautifulSoup(html_ctnt, 'lxml')

items = []

for div in soup.find_all('div', {'class': 'card ng-star-inserted'}):
    imovel = {}

    estate_info_div = div.find('div', {'class': 'card__textbox_container'})
    # print('estate_info_div:', estate_info_div)
    imovel['preco'] = estate_info_div.find('h4', {'class': 'card__price ng-star-inserted'}).string
    
    location_ps = estate_info_div.find_all('p', {'class': 'card__location'})
    imovel['localizacao'] = f'{location_ps[0].string} - {location_ps[1].string}'

    metrics = div.find('ul', {'class': 'attributes'}).find_all('li', {'class', 'attributes__icon-wrapper ng-star-inserted'})

    imovel['tags'] = []

    for m in metrics:
        # lps-icon-ruler -> área total
        # lps-icon-bed -> dormitórios
        # lps-icon-car -> vagas
        # lps-icon-sink -> banheiros
        tag = {}
        tag['valor'] = m.find('div', {'class.attributes__value': 'withLabel'}).string
        
        if m.find('lps-icon-ruler') != None:
            tag['significado'] =  'área total'
        elif m.find('lps-icon-bed') != None:
            tag['significado'] =  'dormitórios'
        elif m.find('lps-icon-car') != None:
            tag['significado'] =  'vagas'
        elif m.find('lps-icon-sink') != None:
            tag['significado'] =  'banheiros'
        else:
            tag['significado'] =  'desconhecido'
        imovel['tags'].append(tag)

    print('Scrapping', imovel)
    # items.append(li)

# print(items)
# df_full = pd.read_html(str(table))[0] # já transforma a table em um data frame com os nomes dos dados
# # print(df_full)
# df_full.to_csv("lopes_imoveis.csv")