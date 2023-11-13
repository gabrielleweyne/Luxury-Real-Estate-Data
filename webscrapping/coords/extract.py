import googlemaps

def find_coords(addr):
    print(f"FINDING COORDS FOR {addr}")
    coords = googlemaps.Client(key='YOUR API KEY').geocode(addr)[0]['geometry']['location']
    print(f"FOUND COORD! {coords}")
    return coords