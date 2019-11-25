import datetime
import numpy as np
import pandas as pd
from pymongo import MongoClient

def historicalUtilizationPercentageWithIgnore(blocks, timestamp, lookbackWeeks, timewindow, client):
    """Return the percent of time a block is open in its past."""
    db = client['parking']

    # Get a list of the deviceIds - .086
    allStreetNames = [x for x in np.unique(blocks['StreetName'])]
    allBetweenStreet1 = [x for x in np.unique(blocks['BetweenStreet1'])]
    allBetweenStreet2 = [x for x in np.unique(blocks['BetweenStreet2'])]

    deviceIdsForBlock =  db.deviceToSpaceAndBlock.find({'StreetName': {'$in': allStreetNames},
                                                        'BetweenStreet1': {'$in': allBetweenStreet1},
                                                        'BetweenStreet2': {'$in': allBetweenStreet2}})
    deviceIdsForBlock = pd.DataFrame(list(deviceIdsForBlock))

    deviceList = [int(x) for x in deviceIdsForBlock['DeviceId']]


    # Create list of timestamps to check
    timeWindows = []
    for i in range(1, lookbackWeeks+1):
        windowOpen = timestamp - datetime.timedelta(days = 7 * i) - datetime.timedelta(minutes = timewindow/2)
        windowClose = timestamp - datetime.timedelta(days = 7 * i) + datetime.timedelta(minutes = timewindow/2)
        timeWindows.append([windowOpen, windowClose])


    maxTime = timeWindows[0][1]
    minTime = timeWindows[lookbackWeeks-1][0]

    # Query for all the blocks over the time of interest
    finder = db.sensorData.find({'DeviceId': {'$in': deviceList},
                                 'ArrivalTime': {'$lte': maxTime},
                                 'DepartureTime': {'$gte': minTime}})

    # Find all events that find within a window, trim them, and label them
    eventsInWindows = []

    for event in finder:
        for window in timeWindows:
            if event['ArrivalTime'] <= window[1] and event['DepartureTime'] >= window[0]:
                if event['ArrivalTime'] < window[0]:
                    event['ArrivalTime'] = window[0]
                if event['DepartureTime'] > window[1]:
                    event['DepartureTime'] = window[1]
                event['windowOpen'] = window[0]
                eventsInWindows.append(event)

    eventsInWindows = pd.DataFrame(eventsInWindows)
    eventsInWindows = eventsInWindows.astype({"Vehicle Present": int})
    eventsInWindows.rename(columns={"Vehicle Present": "VehiclePresent"}, inplace=True)


    predictions = []
    for i in range(0, len(blocks)):

        blockDeviceIds = deviceIdsForBlock[(deviceIdsForBlock['StreetName'] == blocks['StreetName'][i]) & (deviceIdsForBlock['BetweenStreet1'] == blocks['BetweenStreet1'][i]) & (deviceIdsForBlock['BetweenStreet2'] == blocks['BetweenStreet2'][i])]
        blockDeviceIds['DeviceId']

        tmpEvents = eventsInWindows[eventsInWindows['DeviceId'].isin(blockDeviceIds['DeviceId'])]

        openMinutes = 0
        totalMinutes = 0


        # Sum up the availability across each window
        for window in timeWindows:
            df = tmpEvents[tmpEvents['windowOpen'] == window[0]]
            timeChecks = np.sort(np.unique(np.append(df['ArrivalTime'], df['DepartureTime'])))
            numDevices = len(np.unique(df['DeviceId']))

            for i in range(0,len(timeChecks)-1):
                if len(df[(df['ArrivalTime'] <= timeChecks[i]) & (df['DepartureTime'] > timeChecks[i])]) >= numDevices:
                    totalMinutes = totalMinutes + np.timedelta64(timeChecks[i+1] - timeChecks[i], 's').astype(int)/60.
                    if len(df[(df['ArrivalTime'] <= timeChecks[i]) & (df['DepartureTime'] > timeChecks[i]) & (df['VehiclePresent'] == 0)]) > 0:
                        openMinutes = openMinutes + np.timedelta64(timeChecks[i+1] - timeChecks[i], 's').astype(int)/60.

        if totalMinutes == 0:
            prediction = 0
        else:
            prediction = float(openMinutes) / (totalMinutes)

        predictions.append(prediction)

    return(predictions)
