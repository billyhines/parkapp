from geopy.geocoders import Nominatim
from pymongo import MongoClient
import numpy as np
import pandas as pd
import datetime
from dateutil.parser import parse
import predictive_functions2

def geocode_address(locationQuery):
    """Geocode the address. Return the coordinates and clean address."""
    geolocator = Nominatim(user_agent="parkApp")
    location = geolocator.geocode(locationQuery)

    # Check for geocoding success
    if location == None:
        raise ValueError('Address could not be geocoded')

    coordinates = [location.longitude, location.latitude]
    cleanAddress = location.address

    result = {"address": cleanAddress,
              "coordinates": coordinates}

    return(result)

def findCloseBlocks(point, meters, client):
    """Return the blocks within the given radius to the point."""
    db = client['parking']

    # Find markers within the radius
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

    # Check to make sure that there are spaces close to the point of interest
    if len(closeMarkers) == 0:
        raise ValueError('No parking bays found near specified point')

    # Find blocks associated with these close markers
    closeBlocksCur =  db.deviceToSpaceAndBlock.find({'StreetMarker': {'$in': closeMarkers}})
    closeBlocks = []
    for entry in closeBlocksCur:
        closeBlocks.append({'StreetName': entry['StreetName'],
                            'BetweenStreet1': entry['BetweenStreet1'],
                            'BetweenStreet2': entry['BetweenStreet2']})
    closeBlocks = pd.DataFrame(closeBlocks)
    closeBlocks.drop_duplicates(inplace=True)
    return(closeBlocks)

def findBlockCoordinates(block_df, client):
    """Return the space marker ids and their coordinates for markers within the given blocks."""
    db = client['parking']

    # Find all the markers within blocks
    blocksWithAllMarkers = []
    for index, row in block_df.iterrows():
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

    # Find coordinatess for all markers
    markerCoordsCur = db.bayData.find({"properties.marker_id" :{"$in": [x for x in blocksWithAllMarkers['marker_id']]}})

    markerCoords = []
    for marker in markerCoordsCur:
        markerCoords.append({'marker_id': marker['properties']['marker_id'],
                             'coordinates': marker['geometry']['coordinates'],
                             'description': marker['properties']['rd_seg_dsc']})
    markerCoords = pd.DataFrame(markerCoords)

    # Join in the coordinates then format for output
    blocksWithAllMarkers = blocksWithAllMarkers.merge(markerCoords, how = 'left', right_on = 'marker_id', left_on = 'marker_id')
    blocksWithAllMarkers.dropna(inplace=True)

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
    """Return the predicted availablitlity for each block at the given time."""
    db = client['parking']

    # Find the unique blocks
    blocks = []
    for spot in features:
        blocks.append((spot['properties']['StreetName'],
                       spot['properties']['BetweenStreet1'],
                       spot['properties']['BetweenStreet2']))

    blocks = pd.DataFrame(blocks, columns=('StreetName', 'BetweenStreet1', 'BetweenStreet2'))
    blocks.drop_duplicates(inplace = True)

    # Use the current time if the user did not specify a time
    if time == "":
        timestamp = datetime.datetime.now()
    else:
        timestamp = parse(time)

    timestamp = datetime.datetime(2017, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
    lookbackWeeks = 10
    timewindow = 50

    # Run the predictive function for each of the blocks
    predictions = []
    for index, row in blocks.iterrows():
        prediction = predictive_functions2.historicalUtilizationPercentageWithIgnore(row['StreetName'], row['BetweenStreet1'], row['BetweenStreet2'],
                                                                                     timestamp, lookbackWeeks,timewindow, client)
        predictions.append(prediction)

    blocks['prediction'] = predictions

    # Format the output
    for spot in features:
        tmpPrediction = blocks[(blocks['StreetName'] == spot['properties']['StreetName']) &
                               (blocks['BetweenStreet1'] == spot['properties']['BetweenStreet1']) &
                               (blocks['BetweenStreet2'] == spot['properties']['BetweenStreet2'])]['prediction'].values[0]

        if tmpPrediction >= 0.95:
            tmpIsOpen = 'yes'
        else:
            tmpIsOpen = 'no'

        spot['properties']['prediction'] = tmpPrediction
        spot['properties']['isOpen'] = tmpIsOpen

    return(features)
