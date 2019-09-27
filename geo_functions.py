def geocode_address(locationQuery):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="parkApp")

    location = geolocator.geocode(locationQuery)
    coordinates = [location.longitude, location.latitude]

    return(coordinates)
