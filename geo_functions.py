def geocode_address(locationQuery):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="parkApp")

    location = geolocator.geocode(locationQuery)
    coordinates = [location.longitude, location.latitude]

    return(coordinates)

def findCloseParking(point, meters):
    from pymongo import MongoClient
    client = MongoClient()
    db = client['parking']

    closeBays = db.bayData.find({  'geometry': {
                                     '$near': {
                                       '$geometry': {
                                          'type': "Point" ,
                                          'coordinates': [point[0], point[1]]
                                       },
                                       '$maxDistance': meters
                                     }
                                   }
                                })
    return(closeBays)
