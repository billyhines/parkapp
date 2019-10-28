def historicalUtilizationPercentageWithIgnore(StreetName, BetweenStreet1, BetweenStreet2, timestamp, lookbackWeeks, timewindow):

    import datetime
    import numpy as np
    import pandas as pd
    from pymongo import MongoClient
    client = MongoClient()
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

    openMinutes = 0
    totalMinutes = 0

    maxTime = timeWindows[0][1]
    minTime = timeWindows[lookbackWeeks-1][0]

    # One BFQ
    finder = db.sensorData.aggregate([
    {
        '$project': {
            'ArrivalTime': 1,
            'DepartureTime': 1,
            'DeviceId': 1,
            'VehiclePresent': {'$cond': ['$Vehicle Present', 1, 0]},
            '_id': 1
        }
    },
    {
        '$match': {
            'ArrivalTime': {'$lte': maxTime},
            'DepartureTime': {'$gte': minTime},
            'DeviceId': {'$in': deviceList}
        }
    }])

    #Find all events that find within a window, trim them, and label them
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

    # Sum up the availability across each window
    for window in timeWindows:
        df = eventsInWindows[eventsInWindows['windowOpen'] == window[0]]
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