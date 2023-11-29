from .lopes.scraping import webscrapping as lopes_webscrapping

# from vivareal import webscrapping as vivareal_webscrapping
from webscrapping.coords import put_coords
from webscrapping.db import save_to_db
import pandas as pd

if __name__ == "__main__":
    # save_to_db(put_coords(lopes_webscrapping()))
    estates_df = pd.read_csv("ESTATES_BACKUP.csv", sep=";", header=0)
    save_to_db(estates_df, create_csv=False)
