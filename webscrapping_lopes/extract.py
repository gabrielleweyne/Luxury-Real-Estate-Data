import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup  # Parseador de HTML
from url import get_lopes_root_url

listing_xpath = "/html/body/lps-root/lps-search/div/div/div/div/lps-search-grid/lps-search-content/div/div[1]/div[2]/lps-card-grid/div[1]/ul"
max_page_xpath = "/html/body/lps-root/lps-search/div/div/div/div/lps-search-grid/div/lps-pagination/ul/li[8]/span"

def get_estate_page_soup(url, xpath=listing_xpath, return_max_page=False):
    print("Starting up driver...")
    options = webdriver.FirefoxOptions()  # Opções do webdrive
    options.add_argument("-headless")  # Rodar o firefox no terminal

    print(f"Opening url ({url})...")
    driver = webdriver.Firefox(
        options=options
    )  # Por default ele já procura onde o Firefox instalou e onde está o geckodriver
    driver.get(url)  # Bater na página

    print("Waiting load...")
    time.sleep(4)  # esperar 5 segundos para a página carregar

    print("Getting estate list from listing_xpath...")
    el = driver.find_element(By.XPATH, xpath)
    html_ctnt = el.get_attribute("outerHTML")
    soup = BeautifulSoup(html_ctnt, "lxml")

    if not return_max_page:
        driver.quit()  # fechar o navegador
        print("Returning Soup")
        return soup
    
    max_page = int(driver.find_element(By.XPATH, max_page_xpath).text)

    driver.quit()  # fechar o navegador

    return [max_page, soup]



svg_icon_meaning = {
    "lps-icon-ruler": "total area",
    "lps-icon-bed": "dorms",
    "lps-icon-car": "parking",
    "lps-icon-sink": "toilets",
}


def extract_estates_from_soup(page_soup):
    # Pegar os links dos imóveis
    estate_links = list(
        map(
            lambda el: get_lopes_root_url() + el.find("a").get("href"),
            page_soup.find_all("div", {"class": "card ng-star-inserted"}),
        )
    )

    print(f'========= FOUND {len(estate_links)} ESTATES')

    estates_datas = []

    # Extrair os dados dos imóveis das suas respectivas páginas de detalhe
    for link in estate_links:
        estate_data = {"source_id": link.split("/")[4]}

        print("GETTING INFO ON", estate_data["source_id"])
        estate_info_html = get_estate_page_soup(
            link,
            xpath="/html/body/lps-root/lps-product-layout/nav-layout-default/lps-product/div[1]/div[1]/div[1]/div",
        )

        estate_data["address"] = estate_info_html.find(
            "lps-product-address"
        ).div.p.string

        estate_data["price"] = (
            estate_info_html.find("lps-product-price")
            .find("p", {"class": "product-price__body ng-star-inserted"})
            .string
        )

        for attr_li in estate_info_html.find_all(
            "li", {"class": "product-attribute ng-star-inserted"}
        ):
            svg_icon = attr_li.div.find("lps-icon").div.find_all_next()[0].name
            key = svg_icon_meaning.get(svg_icon)
            if key != None:
                # TODO: Fazer uma Regex para extrair apenas os números dos valores
                estate_data[key] = attr_li.find(
                    "div", {"class": "prod uct-attribute__info__value"}
                ).string

        estates_datas.append(estate_data)
        print("FINISHED", estate_data["source_id"])

    return estates_datas
