from geopy.geocoders import Nominatim
from pymongo import MongoClient
from shapely.geometry import MultiPolygon, Polygon, Point
import numpy as np
import pandas as pd
import datetime
from dateutil.parser import parse
import predictive_functions2

def geocode_address(locationQuery):
    geolocator = Nominatim(user_agent="parkApp")

    location = geolocator.geocode(locationQuery)

    if location == None:
        raise AttributeError('Address could not be geocoded')

    coordinates = [location.longitude, location.latitude]
    cleanAddress = location.address

    result = {"address": cleanAddress,
              "coordinates": coordinates}

    return(result)

def findCloseBlocks2(point, meters, client):
    db = client['parking']

    #find close blocks
    closeBays = db.bayData.aggregate([
                                    {'$geoNear': {
                                        'near': { 'type': 'Point', 'coordinates':[point[0], point[1]]},
                                        'key': 'geometry',
                                        'distanceField': 'dist.calculated',
                                        '$maxDistance': meters,
                                        'query': { 'properties.marker_id': {'$ne':None} },
                                        }},
                                    {'$lookup': {
                                        'from': 'deviceToSpaceAndBlock',
                                        'localField': 'properties.marker_id',
                                        'foreignField': 'StreetMarker',
                                        'as': 'markersToBlocks'}},
                                    {"$unwind": "$markersToBlocks" },
                                    {'$project': { 'street_concat': {'$concat': ['$markersToBlocks.StreetName',
                                                                                 '$markersToBlocks.BetweenStreet1',
                                                                                 '$markersToBlocks.BetweenStreet2']}}}])

    closeBlocks = [x['street_concat'] for x in closeBays]
    closeBlocks = list(np.unique(closeBlocks))

    # Check to make sure that there are blocks inside the radius
    if len(closeBlocks) == 0:
        raise AttributeError('No parking bays found near specified point')

    # find the coordinates associate with these blocks
    markersCoords = db.deviceToSpaceAndBlock.aggregate([
                                                    {'$project': {
                                                        'castedStreetName': {'$substrBytes': [ '$StreetName', 0, 128 ]},
                                                        'castedBetweenStreet1': {'$substrBytes': [ '$BetweenStreet1', 0, 128 ]},
                                                        'castedBetweenStreet2': {'$substrBytes': [ '$BetweenStreet2', 0, 128 ]},
                                                        'StreetMarker': 1}},
                                                    {'$project':{'street_concat':{'$concat':["$castedStreetName","$castedBetweenStreet1","$castedBetweenStreet2"]},
                                                                 'StreetMarker': 1,
                                                                 'castedStreetName': 1,
                                                                 'castedBetweenStreet1': 1,
                                                                 'castedBetweenStreet2':1}},
                                                    {'$match':{'street_concat':{'$in': closeBlocks}}},
                                                    {'$lookup': {
                                                        'from': 'bayData',
                                                        'localField': 'StreetMarker',
                                                        'foreignField': 'properties.marker_id',
                                                        'as': 'bayData'}}
                                                    ])
    # format the output
    blocksWithCoords = []
    for entry in markersCoords:
        if len(entry['bayData']) == 0:
            continue
        blocksWithCoords.append({"type": "Feature",
                                 "geometry": {
                                    "type": "MultiPolygon",
                                    "coordinates": entry['bayData'][0]['geometry']['coordinates']},
                                 "properties": {
                                    "StreetName": entry['castedStreetName'],
                                    "BetweenStreet1": entry['castedBetweenStreet1'],
                                    "BetweenStreet2": entry['castedBetweenStreet2'],
                                    "description": entry['bayData'][0]['properties']['rd_seg_dsc']
                                 }})
    return(blocksWithCoords)

def findCloseBlocks(point, meters, client):
    db = client['parking']

    # find close markers
    closeMarkerCur = db.bayData.find({'geometry': {
                                        '$near': {
                                            '$geometry': {
                                                'type': "Point" ,
                                                'coordinates': [point[0], point[1]]},
                                            '$maxDistance': meters}}
                                       })

    closeMarkers = [x['properties']['marker_id'] for x in closeMarkerCur]
    closeMarkers = np.unique(closeMarkers)
    closeMarkers = list(filter(None, closeMarkers))

    # check to make sure that there are spaces close to the point of interest
    if len(closeMarkers) == 0:
        raise AttributeError('No parking bays found near specified point')

    # find blocks with close markers
    closeBlocksCur =  db.deviceToSpaceAndBlock.find({'StreetMarker': {'$in': closeMarkers}})
    closeBlocks = []
    for entry in closeBlocksCur:
        closeBlocks.append({'StreetName': entry['StreetName'],
                            'BetweenStreet1': entry['BetweenStreet1'],
                            'BetweenStreet2': entry['BetweenStreet2']})
    closeBlocks = pd.DataFrame(closeBlocks)
    closeBlocks.drop_duplicates(inplace=True)

    # find all the markers within blocks
    blocksWithAllMarkers = []
    for index, row in closeBlocks.iterrows():
        markersPerBlockCur = db.deviceToSpaceAndBlock.find({'StreetName': row['StreetName'],
                                                            'BetweenStreet1': row['BetweenStreet1'],
                                                            'BetweenStreet2':row['BetweenStreet2']})
        for marker in markersPerBlockCur:
            blocksWithAllMarkers.append({'StreetName': row['StreetName'],
                                         'BetweenStreet1': row['BetweenStreet1'],
                                         'BetweenStreet2': row['BetweenStreet2'],
                                         'marker_id': marker['StreetMarker']})
    blocksWithAllMarkers = pd.DataFrame(blocksWithAllMarkers)
    blocksWithAllMarkers.drop_duplicates(inplace=True)

    # find coordinatess for all markers
    markerCoordsCur = db.bayData.find({"properties.marker_id" :{"$in": [x for x in blocksWithAllMarkers['marker_id']]}})

    markerCoords = []
    for marker in markerCoordsCur:
        markerCoords.append({'marker_id': marker['properties']['marker_id'],
                             'coordinates': marker['geometry']['coordinates'],
                             'description': marker['properties']['rd_seg_dsc']})
    markerCoords = pd.DataFrame(markerCoords)

    blocksWithAllMarkers = blocksWithAllMarkers.merge(markerCoords, how = 'left', right_on = 'marker_id', left_on = 'marker_id')
    blocksWithAllMarkers.dropna(inplace=True)

    # create dict for output
    blocksWithCoords = []
    for index, row in blocksWithAllMarkers.iterrows():
        blocksWithCoords.append({"type": "Feature",
                                 "geometry": {
                                    "type": "MultiPolygon",
                                    "coordinates": row['coordinates']},
                                 "properties": {
                                    "StreetName": row['StreetName'],
                                    "BetweenStreet1": row['BetweenStreet1'],
                                    "BetweenStreet2": row['BetweenStreet2'],
                                    "description": row['description']}})

    return(blocksWithCoords)

def getBlockAvailability(features, time, client):
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

    predictions = []
    for i in range(0, len(blocks)):
        #prediction = predictive_functions.historicalUtilizationPercentageWithIgnore(blocks['StreetName'][i], blocks['BetweenStreet1'][i], blocks['BetweenStreet2'][i], timestamp, lookbackWeeks, timewindow, client)
        prediction = predictive_functions2.historicalUtilizationPercentageWithIgnore(blocks['StreetName'][i], blocks['BetweenStreet1'][i], blocks['BetweenStreet2'][i], timestamp, lookbackWeeks, timewindow, client)
        predictions.append(prediction)

    #predictions = predictive_functions3.historicalUtilizationPercentageWithIgnore(blocks, timestamp, lookbackWeeks, timewindow, client)

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

    return(features)
