
def generate_google_maps_link(place_name):
    base = "https://maps.google.com/?q="
    return base + place_name.replace(" ", "+")
