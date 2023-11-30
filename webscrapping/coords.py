import googlemaps
import pandas as pd


def put_coords(estates_df):
    print("==================> GETTING COORDS ")
    return estates_df.join(
        pd.DataFrame(
            list(map(lambda edf: find_coords(edf[1].address), estates_df.iterrows()))
        )
    )


def find_coords(addr):
    return googlemaps.Client(key="API_KEY").geocode(
        addr
    )[0]["geometry"]["location"]
