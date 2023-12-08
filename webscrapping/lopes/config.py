def get_lopes_root_url():
    return "https://www.lopes.com.br"

def get_lopes_listing_url(page=1):
    if page == 1:
        return "https://www.lopes.com.br/busca/venda/br/sp/sao-paulo?preco-menor=15000000&placeId=ChIJ0WGkg4FEzpQRrlsz_whLqZs"
    else:
        return f"https://www.lopes.com.br/busca/venda/br/sp/sao-paulo/pagina/{page}?preco-menor=15000000&placeId=ChIJ0WGkg4FEzpQRrlsz_whLqZs"
    