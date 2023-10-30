from extract import get_html_soup
from save import save_to_db
import re
import math
import pandas as pd
from datetime import datetime

url = 'https://www.vivareal.com.br/venda/sp/sao-paulo/#onde=Brasil,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,,,,,,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo,,,&preco-desde=15000000'

xpath = '//*[@id="js-site-main"]/div[2]/div[1]/section' # caminho direto para o elemento htlm com a lista dos imóveis

soup = get_html_soup(url, xpath) # pega os imóveis da página

# print(soup)

links = soup.find_all('a', {'class':'property-card__content-link js-card-title'}) # pegar todos os links quebrados que possuem essa classe

# print(links)

root = 'https://www.vivareal.com.br' # parte faltante dos links quebrados

get_link = lambda x: root + x.get('href') # função anônima para juntar o link quebrado com a parte faltante

lista = list(map(get_link, links)) # repassa a lista de links quebrados e para cada um roda a função que junta e no final tranforma em uma lista 

# print(lista)

total_imoveis = (int("".join(re.findall("[0-9]+", soup.find('strong', {'class': "results-summary__count js-total-records"}).string))))

imoveispp = len(lista)

print(imoveispp)

total_paginas = math.ceil(total_imoveis/imoveispp)

print(total_imoveis,imoveispp, total_paginas)

estates = []

for link in lista:
    id = link.split("/")[4]

    dicionario_dados = {
                    "source": "vivareal",
                    "source_id":id,
                    "timestamp":  datetime.now()}

    path =  '//*[@id="js-site-main"]/div[2]' # caminho direto para o elemento html que possui todas as informações dos imóveis que queremos raspar
    dados = get_html_soup(link, path)

    preco = "".join(re.findall("[0-9]+",dados.find('h3', {'class':"price__price-info js-price-sale"}).string))
    if preco == "":
        dicionario_dados['preco'] = None
    else:
        dicionario_dados['preco'] = float(preco)
    print(preco)

    area = dados.find('li', {'class':"features__item features__item--area js-area"}).string
    if area != None:
        dicionario_dados['total area'] = int("".join(re.findall("[0-9]+",area)))
    print(area)

    quartos = dados.find('li', {'class':"features__item features__item--bedroom js-bedrooms"}).string
    if quartos != None:
        dicionario_dados['dorms'] = int("".join(re.findall("[0-9]+",quartos)))
    print(quartos)

    banheiros = dados.find('li', {'class':"features__item features__item--bathroom js-bathrooms"}).string
    if banheiros != None:
        dicionario_dados['toilets'] = int("".join(re.findall("[0-9]+",banheiros)))
    print(banheiros)

    vagas = dados.find('li', {'class':"features__item features__item--parking js-parking"}).string
    if vagas != None:
        dicionario_dados['parking'] = int("".join(re.findall("[0-9]+",vagas)))
    print(vagas)

    endereco = dados.find('p', {'class':"title__address js-address"}).string
    dicionario_dados['address'] = endereco
    print(endereco)
    
    estates.append(dicionario_dados)
    
tabela = pd.DataFrame(estates)

save_to_db(estates, 1) 

print(tabela)

for pagina in range(2, 21):

    estates = []

    url = f'https://www.vivareal.com.br/venda/sp/sao-paulo/?pagina={pagina}#onde=Brasil,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,,,,,,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo,,,&preco-desde=15000000'

    xpath = '//*[@id="js-site-main"]/div[2]/div[1]/section' # caminho direto para o elemento htlm com a lista dos imóveis

    soup = get_html_soup(url, xpath) # pega os imóveis da página

    links = soup.find_all('a', {'class':'property-card__content-link js-card-title'}) # pegar todos os links quebrados que possuem essa classe

    root = 'https://www.vivareal.com.br' # parte faltante dos links quebrados

    get_link = lambda x: root + x.get('href') # função anônima para juntar o link quebrado com a parte faltante

    lista = list(map(get_link, links)) # repassa a lista de links quebrados e para cada um roda a função que junta e no final tranforma em uma lista 

    print(pagina)

    for link in lista:
        id = link.split("/")[2]

        dicionario_dados = {
                    "source": "vivareal",
                    "source_id":id,
                    "timestamp":  datetime.now()}

        path =  '//*[@id="js-site-main"]/div[2]' # caminho direto para o elemento html que possui todas as informações dos imóveis que queremos raspar
        dados = get_html_soup(link, path)

        preco = float("".join(re.findall("[0-9]+", dados.find('h3', {'class':"price__price-info js-price-sale"}).string)))
        print(preco)

        area = dados.find('li', {'class':"features__item features__item--area js-area"}).string
        if area != None:
            dicionario_dados['total area'] = int("".join(re.findall("[0-9]+",area)))
        print(area)

        quartos = dados.find('li', {'class':"features__item features__item--bedroom js-bedrooms"}).string
        if quartos != None:
            dicionario_dados['dorms'] = int("".join(re.findall("[0-9]+",quartos)))
        print(quartos)

        banheiros = dados.find('li', {'class':"features__item features__item--bathroom js-bathrooms"}).string
        if banheiros != None:
            dicionario_dados['toilets'] = int("".join(re.findall("[0-9]+",banheiros)))
        print(banheiros)

        vagas = dados.find('li', {'class':"features__item features__item--parking js-parking"}).string
        if vagas != None:
            dicionario_dados['parking'] = int("".join(re.findall("[0-9]+",vagas)))
        print(vagas)

        endereco = dados.find('p', {'class':"title__address js-address"}).string
        dicionario_dados['address'] = endereco
        print(endereco)
    
        estates.append(dicionario_dados)
    
    tabela = pd.DataFrame(estates)
    save_to_db(estates, pagina) 
