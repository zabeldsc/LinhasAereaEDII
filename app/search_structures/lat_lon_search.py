from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="companhia_aerea_app")

def buscar_coordenada(local):
    location = geolocator.geocode(local)
    
    if location:
        return [location.latitude, location.longitude]
    return None