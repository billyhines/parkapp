def geocode_address(locationQuery):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="parkApp")

    location = geolocator.geocode(locationQuery)
    coordinates = [location.longitude, location.latitude]

    return(coordinates)

def getBlockPolygon(StreetName, BetweenStreet1, BetweenStreet2):
    from pymongo import MongoClient
    from shapely.geometry import MultiPolygon, Polygon, Point
    client = MongoClient()
    db = client['parking']

    markers =  db.deviceToSpaceAndBlock.find({  'StreetName': StreetName,
                                                'BetweenStreet1': BetweenStreet1,
                                                'BetweenStreet2': BetweenStreet2})

    markerIds = [x['StreetMarker'] for x in markers]

    spaceData = db.bayData.find({"properties.marker_id" :{"$in": markerIds}})

    spacePolys = []

    for space in spaceData:
        coords = [(p[0], p[1]) for p in space['geometry']['coordinates'][0][0]]
        #tmpPoly = Polygon(coords)
        #spacePolys.append(tmpPoly)
        spacePolys.append(coords)

    #blockMulti = MultiPolygon(spacePolys)

    #return(blockMulti)
    return(spacePolys)

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


def findCloseBlocks(point, meters):
    from pymongo import MongoClient
    import numpy as np
    import pandas as pd
    client = MongoClient()
    db = client['parking']

    # find close markers
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

    markerIds = [x['properties']['marker_id'] for x in closeBays]
    markerIds = np.unique(markerIds)
    markerIds = list(filter(None, markerIds))

    # find blocks with close markers
    blocksAndMarkers =  db.deviceToSpaceAndBlock.find({'StreetMarker': {'$in': markerIds}})
    blocksAndMarkers = pd.DataFrame(list(blocksAndMarkers))
    blocks = blocksAndMarkers[['StreetName', 'BetweenStreet1', 'BetweenStreet2']].drop_duplicates()
    blocks.reset_index(inplace=True)

    # find all markers within blocks
    blockMarkers = []
    for i in range(0, len(blocks)):
        markersPerBlock = db.deviceToSpaceAndBlock.find({'StreetName': blocks['StreetName'][i],
                                                         'BetweenStreet1': blocks['BetweenStreet1'][i],
                                                         'BetweenStreet2':blocks['BetweenStreet2'][i]})
        markersPerBlock = [x['StreetMarker']for x in markersPerBlock]
        tmp = pd.DataFrame({'marker_id': np.unique(markersPerBlock)})
        tmp['StreetName'] = blocks['StreetName'][i]
        tmp['BetweenStreet1'] = blocks['BetweenStreet1'][i]
        tmp['BetweenStreet2'] = blocks['BetweenStreet2'][i]
        blockMarkers.append(tmp)
    blockMarkers = pd.concat(blockMarkers, ignore_index = True)

    # find coords for all markers
    markerCoords = db.bayData.find({"properties.marker_id" :{"$in": [x for x in blockMarkers['marker_id']]}})

    coords = []
    ids = []
    desc = []
    for marker in markerCoords:
        coords.append(marker['geometry']['coordinates'])
        ids.append(marker['properties']['marker_id'])
        desc.append(marker['properties']['rd_seg_dsc'])

    markerCoords = pd.DataFrame({'marker_id':ids,
                                 'coordinates': coords,
                                 'description': desc})
    blockMarkers = blockMarkers.merge(markerCoords, how = 'left', right_on = 'marker_id', left_on = 'marker_id')
    blockMarkers.dropna(inplace=True)
    blockMarkers.reset_index(inplace=True)
    # create dict for output

    blocksWithCoords = []

    for i in range(0, len(blockMarkers)):
        blockName = blockMarkers['StreetName'][i] + ' between ' + blockMarkers['BetweenStreet1'][i] + ' and ' + blockMarkers['BetweenStreet2'][i]
        blocksWithCoords.append({"type": "Feature",
                                 "geometry": {
                                    "type": "MultiPolygon",
                                    "coordinates": blockMarkers['coordinates'][i]},
                                 "properties": {
                                    "block": blockName,
                                    "description": blockMarkers['description'][i]
                                 }})

    return(blocksWithCoords)
