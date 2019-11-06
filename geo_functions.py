from geopy.geocoders import Nominatim
from pymongo import MongoClient
from shapely.geometry import MultiPolygon, Polygon, Point
import numpy as np
import pandas as pd
import datetime
from dateutil.parser import parse
import predictive_functions3

def geocode_address(locationQuery):
    geolocator = Nominatim(user_agent="parkApp")

    location = geolocator.geocode(locationQuery)

    if location == None:
        raise AttributeError('No results found from geocoder')

    coordinates = [location.longitude, location.latitude]
    cleanAddress = location.address

    result = {"address": cleanAddress,
              "coordinates": coordinates}

    return(result)

def getBlockPolygon(StreetName, BetweenStreet1, BetweenStreet2):
    client = MongoClient()
    db = client['parking']

    markers =  db.deviceToSpaceAndBlock.find({'StreetName': StreetName,
                                              'BetweenStreet1': BetweenStreet1,
                                              'BetweenStreet2': BetweenStreet2})

    markerIds = [x['StreetMarker'] for x in markers]
    spaceData = db.bayData.find({"properties.marker_id" :{"$in": markerIds}})
    spacePolys = []

    for space in spaceData:
        coords = [(p[0], p[1]) for p in space['geometry']['coordinates'][0][0]]
        spacePolys.append(coords)

    client.close()
    return(spacePolys)

def findCloseBlocks(point, meters):
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

    if len(markerIds) == 0:
        raise AttributeError('No parking bays found near specified point')

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
        blocksWithCoords.append({"type": "Feature",
                                 "geometry": {
                                    "type": "MultiPolygon",
                                    "coordinates": blockMarkers['coordinates'][i]},
                                 "properties": {
                                    "StreetName": blockMarkers['StreetName'][i],
                                    "BetweenStreet1": blockMarkers['BetweenStreet1'][i],
                                    "BetweenStreet2": blockMarkers['BetweenStreet2'][i],
                                    "description": blockMarkers['description'][i]
                                 }})

    client.close()
    return(blocksWithCoords)

def getBlockAvailability(features, time):
    client = MongoClient()
    db = client['parking']

    blocks = []
    for i in range(0, len(features)):
        blocks.append((features[i]['properties']['StreetName'], features[i]['properties']['BetweenStreet1'], features[i]['properties']['BetweenStreet2']))

    blocks = pd.DataFrame(blocks, columns=('StreetName', 'BetweenStreet1', 'BetweenStreet2'))
    blocks.drop_duplicates(inplace = True)
    blocks.reset_index(inplace = True)

    if time == "":
        timestamp = datetime.datetime.now()
    else:
        timestamp = parse(time)

    timestamp = datetime.datetime(2017, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
    lookbackWeeks = 10
    timewindow = 50

    #predictions = []
    #for i in range(0, len(blocks)):
        #prediction = predictive_functions.historicalUtilizationPercentageWithIgnore(blocks['StreetName'][i], blocks['BetweenStreet1'][i], blocks['BetweenStreet2'][i], timestamp, lookbackWeeks, timewindow, client)
        #prediction = predictive_functions2.historicalUtilizationPercentageWithIgnore(blocks['StreetName'][i], blocks['BetweenStreet1'][i], blocks['BetweenStreet2'][i], timestamp, lookbackWeeks, timewindow, client)
        #predictions.append(prediction)

    predictions = predictive_functions3.historicalUtilizationPercentageWithIgnore(blocks, timestamp, lookbackWeeks, timewindow, client)

    blocks['prediction'] = predictions
    blocks['isOpen'] = np.where(blocks['prediction']>=0.95, 'yes', 'no')

    for i in range(0, len(features)):
        tmpStreetName = features[i]['properties']['StreetName']
        tmpBetweenStreet1 = features[i]['properties']['BetweenStreet1']
        tmpBetweenStreet2 = features[i]['properties']['BetweenStreet2']
        tmpPrediction = blocks[(blocks['StreetName'] == tmpStreetName) & (blocks['BetweenStreet1'] == tmpBetweenStreet1) & (blocks['BetweenStreet2'] == tmpBetweenStreet2)]['prediction'].values[0]
        tmpIsOpen = blocks[(blocks['StreetName'] == tmpStreetName) & (blocks['BetweenStreet1'] == tmpBetweenStreet1) & (blocks['BetweenStreet2'] == tmpBetweenStreet2)]['isOpen'].values[0]

        features[i]['properties']['prediction'] = tmpPrediction
        features[i]['properties']['isOpen'] = tmpIsOpen

    client.close()
    return(features)
