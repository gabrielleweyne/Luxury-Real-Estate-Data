import pandas as pd
import numpy as np
from models.estate import Estate
from models.estates_ind import EstatesInd
from models.favourite import Favourite
from models.user import User
from models import session, create_models

create_models()

def save_to_db(estates_df, create_csv=True):
    estates_df = estates_df.replace({np.nan: None})
    if create_csv:
        estates_df.to_csv("ESTATES_BACKUP.csv", sep=";")

    for _ind, estate_dict in list(estates_df.iterrows()):
        estates_ind = (
            session.query(EstatesInd)
            .filter_by(source_id=estate_dict["source_id"])
            .first()
        )

        if estates_ind == None:
            estates_ind = EstatesInd(source_id=estate_dict["source_id"])
            session.add(estates_ind)
            session.commit()

        estate = Estate(
            address=estate_dict["address"],
            dorms=estate_dict["dorms"],
            lat=estate_dict["lat"],
            lng=estate_dict["lng"],
            parking=estate_dict["parking"],
            price=estate_dict["price"],
            toilets=estate_dict["toilets"],
            source=estate_dict["source"],
            source_id=estate_dict["source_id"],
            timestamp=estate_dict["timestamp"],
            total_area=estate_dict["total area"],
            img=estate_dict["image"],
            estates_ind_id=estates_ind.id,
        )
        session.add(estate)
        session.commit()
