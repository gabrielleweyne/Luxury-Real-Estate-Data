from extract import get_html_soup, extract_estates_from_soup
from save import save_to_db
import pandas as pd  # manipulação de dados

lopes_url_root = "https://www.lopes.com.br"
listing_url = f"{lopes_url_root}/busca/venda/br/sp/sao-paulo?preco-menor=15000000&placeId=ChIJ0WGkg4FEzpQRrlsz_whLqZs&origem=search"
listing_xpath = "/html/body/lps-root/lps-search/div/div/div/div/lps-search-grid/lps-search-content/div/div[1]/div[2]/lps-card-grid/div[1]/ul"


# TODO: Fazer um loop para pegar a listagem de X páginas
print("GETTING ESTATE LIST FROM " + listing_url)
soup = get_html_soup(listing_url, listing_xpath)

estates_datas = extract_estates_from_soup(soup, lopes_url_root)

# Transformar em um dataframe
df = pd.DataFrame(estates_datas)

# Criar um csv para usar durante o desenvolvimento
df.to_csv("lopes_imoveis.csv")
# df = pd.read_csv('lopes_imoveis.csv')

save_to_db(df)
