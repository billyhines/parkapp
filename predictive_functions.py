import datetime
import numpy as np
import pandas as pd
import itertools
from pymongo import MongoClient
import pymongo.cursor

def historicalUtilizationPercentageWithIgnore(StreetName, BetweenStreet1, BetweenStreet2, timestamp, lookbackWeeks, timewindow, client):
    db = client['parking']

    # get a list of the deviceIds
    deviceList =  db.deviceToSpaceAndBlock.find({'StreetName': StreetName,
                                                 'BetweenStreet1': BetweenStreet1,
                                                 'BetweenStreet2': BetweenStreet2})

    deviceList = [x['DeviceId'] for x in deviceList]
    deviceList = [int(x) for x in deviceList]
    #deviceList = np.unique(deviceList)

    #create list of timestamps to check
    timeWindows = []
    for i in range(1, lookbackWeeks+1):
        windowOpen = timestamp - datetime.timedelta(days = 7 * i) - datetime.timedelta(minutes = timewindow/2)
        windowClose = timestamp - datetime.timedelta(days = 7 * i) + datetime.timedelta(minutes = timewindow/2)
        timeWindows.append([windowOpen, windowClose])

    # intialize time counter variables
    openMinutes = 0
    totalMinutes = 0

    # create a list of finders
    finderlist = [db.sensorData.find({'ArrivalTime': {'$lte': window[1]},
                                      'DepartureTime': {'$gte': window[0]},
                                      'DeviceId': {'$in': deviceList}},
                                      cursor_type=pymongo.cursor.CursorType.EXHAUST,
                                      batch_size=1000) for window in timeWindows]


    # Check the space for each of the windows
    for finder,window in itertools.izip(finderlist,timeWindows):

        df = []
        for event in finder:
            if event['ArrivalTime'] < window[0]:
                event['ArrivalTime'] = window[0]
            if event['DepartureTime'] > window[1]:
                event['DepartureTime'] = window[1]
            df.append(event)
        df = pd.DataFrame(df)

        df = df.astype({"Vehicle Present": int})
        df.rename(columns={"Vehicle Present": "VehiclePresent"}, inplace=True)

        if len(df) == 0:
            continue
        df.loc[df['ArrivalTime'] < window[0], 'ArrivalTime'] = window[0]
        df.loc[df['DepartureTime'] > window[1], 'DepartureTime'] = window[1]

        timeChecks = np.sort(np.unique(np.append(df['ArrivalTime'], df['DepartureTime'])))

        numDevices = len(np.unique(df['DeviceId']))

        for i in range(0,len(timeChecks)-1):

            if len(df[(df['ArrivalTime'] <= timeChecks[i]) & (df['DepartureTime'] > timeChecks[i])]) >= numDevices:
                totalMinutes = totalMinutes + np.timedelta64(timeChecks[i+1] - timeChecks[i], 's').astype(int)/60.
                if len(df[(df['ArrivalTime'] <= timeChecks[i]) & (df['DepartureTime'] > timeChecks[i]) & (df['VehiclePresent'] == 0)]) > 0:
                    openMinutes = openMinutes + np.timedelta64(timeChecks[i+1] - timeChecks[i], 's').astype(int)/60.

    if totalMinutes == 0:
        return(0)
    else:
        return(float(openMinutes) / (totalMinutes))
