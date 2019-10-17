import geo_functions

address = '252 Swanston St Melbourne Australia'
time = '2019-10-30T11:58'

features = []
user_point = geo_functions.geocode_address(address)
closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150)
features.extend(closeBlocks)

featuresWithPrediction = getBlockAvailability(features, time)
featuresWithPrediction



def getBlockAvailability(features, time):

    import pandas as pd
    import numpy as np
    import datetime
    from dateutil.parser import parse
    import predictive_functions

    blocks = []
    for i in range(0, len(features)):
        blocks.append((features[i]['properties']['StreetName'], features[i]['properties']['BetweenStreet1'], features[i]['properties']['BetweenStreet2']))

    blocks = pd.DataFrame(blocks, columns=('StreetName', 'BetweenStreet1', 'BetweenStreet2'))
    blocks.drop_duplicates(inplace = True)
    blocks.reset_index(inplace = True)

    if time == "":
        timestamp = datetime.datetime.now()
        timestamp = datetime.datetime(2017, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
    else:
        timestamp = parse(time)
    lookbackWeeks = 10
    timewindow = 50

    predictions = []
    for i in range(0, len(blocks)):
        prediction = predictive_functions.historicalUtilizationPercentageWithIgnore(blocks['StreetName'][i], blocks['BetweenStreet1'][i], blocks['BetweenStreet2'][i], timestamp, lookbackWeeks, timewindow)
        predictions.append(prediction)


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
