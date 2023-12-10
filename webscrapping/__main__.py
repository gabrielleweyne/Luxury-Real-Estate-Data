from .lopes.scraping import webscrapping as lopes_webscrapping
from .vivareal.scrapping import webscrapping as vivareal_webscrapping
from webscrapping.coords import put_coords
from webscrapping.db import save_to_db
from .add_type_district import add_type_district
import pandas as pd

if __name__ == "__main__":
    save_to_db(put_coords(add_type_district(vivareal_webscrapping(lopes_webscrapping()))))
    # estates_df = pd.read_csv("ESTATES_BACKUP.csv", sep=";", header=0)
    # save_to_db(estates_df, create_csv=False)
    # add_type_district()
