from extract import get_estate_page_soup, extract_estates_from_soup
from save import save_to_db
from url import get_lopes_listing_url

print("========= EXTRACTING ESTATES: PAGE 1 =========")
[max_page, soup] = get_estate_page_soup(get_lopes_listing_url(), return_max_page=True)

estates_datas = extract_estates_from_soup(soup)

save_to_db(extract_estates_from_soup(get_estate_page_soup(get_lopes_listing_url(1))))

for page in range(2, max_page + 1):
    print(f"========= EXTRACTING ESTATES: PAGE {page} OF {max_page} =========")
    save_to_db(
        extract_estates_from_soup(get_estate_page_soup(get_lopes_listing_url(page)))
    )
