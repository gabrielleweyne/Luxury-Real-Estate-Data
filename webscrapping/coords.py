import googlemaps
import pandas as pd


def put_coords(estates_df):
    return estates_df.join(
        pd.DataFrame(
            list(map(lambda edf: find_coords(edf[1].address), estates_df.iterrows()))
        )
    )


def find_coords(addr):
    return googlemaps.Client(key="AIzaSyDi3oATpkJ1USNDDWxb_oID8n01Mv9n3eM").geocode(
        addr
    )[0]["geometry"]["location"]
