import db
import pandas as pd  # manipulação de dados
import re
from extract import find_cep

print("==========READING ESTATES FROM DB==========")
estates_df = db.read_all_from_db()

print(f"FOUND {len(estates_df)} ESTATES")

addrs = pd.DataFrame(list(map(lambda e: find_cep("".join(("".join(re.findall("\D", e[1].address))).split("-")[::2])), estates_df.iterrows())))

new_estates_df = estates_df.join(addrs)

db.save_to_db(new_estates_df)

