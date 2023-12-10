import pandas as pd
from unidecode import unidecode

type_list = ["predio", "apartamento", "casa", "terreno", "lote"]
district_list = list(
    map(
        lambda d: unidecode(d),
        [
            "brooklin",
            "parque novo mundo",
            "bom retiro",
            "brás",
            "ibirapuera",
            "cambuci",
            "campo grande",
            "campo belo",
            "santo amaro",
            "capelinha",
            "casa verde",
            "jardins",
            "cerqueira césar",
            "cidade tiradentes",
            "colonia",
            "cidade jardim",
            "caxingui",
            "pinheiros",
            "jardim santa fé",
            "grajaú",
            "granja julieta",
            "vila gomes cardim",
            "higienópolis",
            "indianópolis",
            "interlagos",
            "ipiranga",
            "itaim bibi",
            "consolação",
            "jardim amália",
            "jardim américa",
            "jardim boa vista",
            "jardim europa",
            "jardim iva",
            "jardim marajoara",
            "jardim paulista",
            "jardim vera cruz",
            "jardim vista alegre",
            "liberdade",
            "jar",
            "luz",
            "jardim cordeiro",
            "moema",
            "morumbi",
            "mooca",
            "pacaembu",
            "paraíso",
            "parque vitória",
            "piraporinha",
            "planalto paulista",
            "república",
            "vila são francisco",
            "santa cecília",
            "santa ifigênia",
            "santa teresinha",
            "santana",
            "sé",
            "tatuapé",
            "vila suzana",
            "vila celeste",
            "vila nova conceição",
            "vila cruzeiro",
            "vila esperança",
            "vila formosa",
            "vila guilherme",
            "vila mariana",
            "vila pompeia",
            "vila santa isabel",
            "tremembé",
            "jardim guedala",
            "jardim paulistano",
            "vila olímpia",
            "vila leopoldina",
            "alto da boa vista",
            "parque anhanguera",
            "jardim panorama",
            "chácara flora",
            "são judas",
            "jaguaré",
            "vila uberabinha",
            "vila prudente",
            "barra funda",
            "água fria",
            "cangaíba",
            "chácara santo antônio",
            "tucuruvi",
            "panamby",
            "conceição",
            "bosque da saúde",
            "vila hamburguesa",
            "bela vista",
            "vila sofia",
            "jardim das laranjeiras",
        ],
    )
)


def add_type_district(estates_df):
    return estates_df.join(
        pd.DataFrame(
            list(map(lambda edf: find_type_district(edf[1]), estates_df.iterrows()))
        )
    )


def find_type_district(estate):
    type_district = {"type": None, "district": None}

    for type in type_list:
        if parse2str(estate.source_id).find(type) >= 0:
            if type == "lote":
                type_district["type"] = "terreno"
                break
            else:
                type_district["type"] = type
                break

    for district in district_list:
        if parse2str(estate.address).find(district) >= 0:
            if district == "jardim paulisantano":
                type_district["district"] = "jardim paulistano"
                break
            else:
                type_district["district"] = district
                break

    return type_district


def parse2str(input):
    return str(input).lower().replace("-", " ")
