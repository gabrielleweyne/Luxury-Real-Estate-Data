from extract import get_estate_page_soup, extract_estates_from_soup
from save import save_to_db
from url import get_lopes_listing_url
import pandas as pd  # manipulação de dados

print("========= EXTRACTING ESTATES: PAGE 1 =========")
[max_page, soup] = get_estate_page_soup(get_lopes_listing_url(), return_max_page=True)

estates_datas = extract_estates_from_soup(soup)

for page in range(2, max_page+1):
    print(f"========= EXTRACTING ESTATES: PAGE {page} OF {max_page} =========")
    next_page_url = get_lopes_listing_url(page)
    page_soup = get_estate_page_soup(next_page_url)
    estates_datas += extract_estates_from_soup(page_soup)

    # Transformar em um dataframe
    df = pd.DataFrame(estates_datas)
    # Criar um csv para usar durante o desenvolvimento
    df.to_csv(f"lopes_imoveis{page}.csv")
    # df = pd.read_csv(f"lopes_imoveis{page}.csv")
    save_to_db(df)
