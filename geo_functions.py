from geopy.geocoders import Nominatim
import numpy as np
import pandas as pd
import datetime
from dateutil.parser import parse
import predictive_functions
from pymongo import MongoClient

def geocode_address(locationQuery):
    """Lookup user inputted text with a Geolocation service. Return the clean address and coordinates.

    :param locationQuery: The address entered by the user.
    :type locationQuery: str
    :returns:  dict -- the cleaned address and coordinates in a dict.
    :raises: ValueError
    """
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
    """Find the blocks in the parking database that are within a given radius to a set of coordinates.

    :param point: The coordinates of the point.
    :type point: list
    :param meters: The radius to search within in meters.
    :type meters: int
    :param client: The pymongo MongoClient instance.
    :type client: pymongo.mongo_client.MongoClient
    :returns:  DataFrame -- the close blocks in a Pandas DataFrame.
    :raises: ValueError, TypeError
    """

    # check to make sure the client variable is a mongo connection
    if type(client) != MongoClient:
        raise ValueError('client must be a MongoClient object')

    # Find markers within the radius
    closeMarkers = findCloseMarker_ids(point, meters, client)

    # Find blocks associated with these close markers
    closeBlocks = blocksFromMarker_ids(closeMarkers, client)

    return(closeBlocks)

def findBlockCoordinates(block_df, client):
    """Return the space marker ids, their coordinates, and block information for markers within the given blocks.

    :param block_df: The close blocks in a Pandas DataFrame.
    :type block_df: DataFrame
    :param client: The pymongo MongoClient instance.
    :type client: pymongo.mongo_client.MongoClient.
    :returns:  list -- a list of Dicts that have all the plotting information for the spaces.
    :raises: ValueError
    """

    # check to make sure the client variable is a mongo connection
    if type(client) != MongoClient:
        raise ValueError('client must be a MongoClient object')

    # Find all the markers within blocks
    blocksWithAllMarkers = marker_idsFromBlocks(block_df, client)
    allMarkers = [x for x in blocksWithAllMarkers['marker_id']]

    # Find coordinatess for all markers
    markerCoords = findCoordsFromMarker_Ids(allMarkers, client)

    # Join blocks and marker information into a common DataFrame
    blocksWithAllMarkers = blocksWithAllMarkers.merge(markerCoords, how = 'left', right_on = 'marker_id', left_on = 'marker_id')
    blocksWithAllMarkers.dropna(inplace=True)

    # Format output into a dict
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
    """Find the predicted availablity for each block and append the information to the list of blocks.

    :param features: A list of Dicts that have all the plotting information for the spaces.
    :type features: list
    :param time: The time entered by the user.
    :type time: str
    :param client: The pymongo MongoClient instance.
    :type client: pymongo.mongo_client.MongoClient.
    :returns:  list -- a list of Dicts that have all the plotting information for the spaces as well as the predictions.
    """
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
        prediction = predictive_functions.historicalUtilizationPercentageWithIgnore(row['StreetName'], row['BetweenStreet1'], row['BetweenStreet2'],
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

def findCloseMarker_ids(point, meters, client):
    """Find the marker_ids for spaces within the radius of the supplied coordinates with a GeoQuery.

    :param point: The coordinates of the point.
    :type point: list
    :param meters: The radius to search within in meters.
    :type meters: int
    :param client: The pymongo MongoClient instance.
    :type client: pymongo.mongo_client.MongoClient
    :returns:  list -- the close marker_ids in a list.
    :raises: ValueError
    """

    # set the database
    db = client['parking']

    # Check for coordinates are correct
    if type(point) != list:
        raise TypeError('point must be a list of Long, Lat')
    if len(point) != 2:
        raise ValueError('point must have a length of two')

    # GeoQuery in the bayData collection for marker_ids
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

    return(closeMarkers)

def blocksFromMarker_ids(closeMarkers, client):
    """Find that blocks that contain the given marker_ids.

    :param closeMarkers: List of marker_ids.
    :type point: list
    :param client: The pymongo MongoClient instance.
    :type client: pymongo.mongo_client.MongoClient
    :returns:  DataFrame -- the close blocks in a Pandas DataFrame.
    :raises: ValueError
    """

    # set the database
    db = client['parking']

    # Find blocks associated with these close markers
    closeBlocksCur =  db.deviceToSpaceAndBlock.find({'StreetMarker': {'$in': closeMarkers}})
    closeBlocks = []
    for entry in closeBlocksCur:
        closeBlocks.append({'StreetName': entry['StreetName'],
                            'BetweenStreet1': entry['BetweenStreet1'],
                            'BetweenStreet2': entry['BetweenStreet2']})
    closeBlocks = pd.DataFrame(closeBlocks)
    closeBlocks.drop_duplicates(inplace=True)

    if len(closeBlocks) == 0:
        raise ValueError('No parking bays found near specified point')

    return(closeBlocks)

def marker_idsFromBlocks(block_df, client):
    """Appends a column of all the marker_ids to a DataFrame of block identifiers.

    :param block_df: The close blocks in a Pandas DataFrame.
    :type block_df: DataFrame
    :param client: The pymongo MongoClient instance.
    :type client: pymongo.mongo_client.MongoClient.
    :returns:  DataFrame -- all of the blocks and the marker_ids assiated with them.
    :raises: ValueError
    """

    db = client['parking']

    # Check for columns in block_df are correct
    if ('BetweenStreet1' not in block_df.columns.values) | ('BetweenStreet2' not in block_df.columns.values) | ('StreetName' not in block_df.columns.values):
        raise ValueError('block_df must have columns for StreetName, BetweenStreet1, and BetweenStreet2')

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

    # Check to make sure that there are maker_ids within the blocks
    if len(blocksWithAllMarkers) == 0:
        raise ValueError('No marker_ids found to be associated with the blocks')

    blocksWithAllMarkers = pd.DataFrame(blocksWithAllMarkers)
    blocksWithAllMarkers.drop_duplicates(inplace=True)
    blocksWithAllMarkers.reset_index(inplace=True, drop=True)

    return(blocksWithAllMarkers)

def findCoordsFromMarker_Ids(marker_ids, client):
    """Returns a DataFrame of marker_ids, coordinates, and desctiptions from the bayData collection

    :param marker_ids: marker_ids of interest
    :type marker_ids: list
    :param client: The pymongo MongoClient instance.
    :type client: pymongo.mongo_client.MongoClient.
    :returns:  DataFrame -- a DataFrame with marker_id, coordinates, and descriptions.
    """

    db = client['parking']

    # Find coordinatess for all markers
    markerCoordsCur = db.bayData.find({"properties.marker_id" :{"$in": marker_ids}})

    markerCoords = []
    for marker in markerCoordsCur:
        markerCoords.append({'marker_id': marker['properties']['marker_id'],
                             'coordinates': marker['geometry']['coordinates'],
                             'description': marker['properties']['rd_seg_dsc']})
    markerCoords = pd.DataFrame(markerCoords)

    return(markerCoords)
