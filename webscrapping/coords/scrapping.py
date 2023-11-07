import db
import pandas as pd  # manipulação de dados
from extract import find_coords

print("==========READING ESTATES FROM DB==========")
estates_df = db.read_all_from_db()

print(f"FOUND {len(estates_df)} ESTATES")

coords = pd.DataFrame(list(map(lambda edf: find_coords(edf[1].address), estates_df.iterrows())))

new_estates_df = estates_df.join(coords)

db.save_to_db(new_estates_df)
