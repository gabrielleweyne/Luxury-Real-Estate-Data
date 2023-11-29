from .extract import get_estate_page_soup, extract_estates_from_soup
from .config import get_lopes_listing_url
from tqdm import tqdm
import pandas as pd


def webscrapping():
    print("========= EXTRACTING ESTATES: PAGE 1 =========")
    [max_page, soup] = get_estate_page_soup(
        get_lopes_listing_url(), return_max_page=True
    )

    estates_data = extract_estates_from_soup(soup)

    # for page in tqdm(range(2, max_page + 1)):
    for page in range(2, 2):
        print(f"========= EXTRACTING ESTATES: PAGE {page} OF {max_page} =========")
        estates_data.append(
            extract_estates_from_soup(get_estate_page_soup(get_lopes_listing_url(page)))
        )

    return pd.DataFrame(estates_data)
