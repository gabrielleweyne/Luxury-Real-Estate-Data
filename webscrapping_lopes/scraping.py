from extract import get_html_soup
from save import save_to_db
import pandas as pd # manipulação de dados

lopes_url_root = 'https://www.lopes.com.br'
listing_url = f'{lopes_url_root}/busca/venda/br/sp/sao-paulo?preco-menor=15000000&placeId=ChIJ0WGkg4FEzpQRrlsz_whLqZs&origem=search'
listing_xpath = '/html/body/lps-root/lps-search/div/div/div/div/lps-search-grid/lps-search-content/div/div[1]/div[2]/lps-card-grid/div[1]/ul'
svg_icon_meaning = {
    'lps-icon-ruler': 'total area',
    'lps-icon-bed': 'dorms',
    'lps-icon-car': 'parking',
    'lps-icon-sink': 'toilets'
}

# TODO: Fazer um loop para pegar a listagem de X páginas
print('GETTING ESTATE LIST FROM ' + listing_url)
soup = get_html_soup(listing_url, listing_xpath)

# Pegar os links dos imóveis
estate_links = list(map(lambda el: lopes_url_root + el.find('a').get('href'), soup.find_all('div', {'class': 'card ng-star-inserted'})))

estates_datas = []

# Extrair os dados dos imóveis das suas respectivas páginas de detalhe
for link in estate_links:
    estate_data = {'source_id': link.split('/')[4]}

    print('GETTING INFO ON', estate_data['source_id'])
    estate_info_html = get_html_soup(link, '/html/body/lps-root/lps-product-layout/nav-layout-default/lps-product/div[1]/div[1]/div[1]/div')
    
    estate_data['address'] = estate_info_html.find('lps-product-address').div.p.string
    
    estate_data['price'] = estate_info_html.find('lps-product-price').find('p', {'class': 'product-price__body ng-star-inserted'}).string
    
    for attr_li in estate_info_html.find_all('li', {'class': 'product-attribute ng-star-inserted'}):
         svg_icon = attr_li.div.find('lps-icon').div.find_all_next()[0].name
         key = svg_icon_meaning.get(svg_icon)
         if key != None:
            # TODO: Fazer uma Regex para extrair apenas os números dos valores
            estate_data[key] = attr_li.find('div', {'class': 'prod uct-attribute__info__value'}).string

    estates_datas.append(estate_data)
    print('FINISHED', estate_data['source_id'], ' ==> ', estate_data)

# Transformar em um dataframe
df = pd.DataFrame(estates_datas)

# Criar um csv para usar durante o desenvolvimento
df.to_csv("lopes_imoveis.csv")
# df = pd.read_csv('lopes_imoveis.csv')

save_to_db(df)