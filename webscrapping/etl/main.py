import db
import pandas as pd  # manipulação de dados

print("==========READING ESTATES FROM DB==========")
estates_df = db.read_all_from_db()

print(f"FOUND {len(estates_df)} ESTATES")

unique_estates = pd.DataFrame({'source_id': estates_df.source_id.unique()})

db.save_to_db(unique_estates)
