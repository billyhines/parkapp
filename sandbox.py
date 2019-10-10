import geo_functions
import predictive_functions


address = '252 Swanston St Melbourne Australia'
#address = request.get_json()['address']

features = []
user_point = geo_functions.geocode_address(address)
features.append({   "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": user_point}})

closeBlocks = geo_functions.findCloseBlocks(user_point, 150)
features.extend(closeBlocks)


#def getBlockAvailability(features):

import pandas as pd
import numpy as np
import datetime
import predictive_functions

blocks = []
for i in range(1, len(features)):
    blocks.append((features[i]['properties']['StreetName'], features[i]['properties']['BetweenStreet1'], features[i]['properties']['BetweenStreet2']))

blocks = pd.DataFrame(blocks, columns=('StreetName', 'BetweenStreet1', 'BetweenStreet2'))
blocks.drop_duplicates(inplace = True)
blocks.reset_index(inplace = True)

timestamp = datetime.datetime.now()
timestamp = datetime.datetime(2017, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
lookbackWeeks = 10
timewindow = 50

predictions = []
for i in range(0, len(blocks)):
    prediction = predictive_functions.historicalUtilizationPercentageWithIgnore(blocks['StreetName'][i], blocks['BetweenStreet1'][i], blocks['BetweenStreet2'][i], timestamp, lookbackWeeks, timewindow)
    predictions.append(prediction)


blocks['prediction'] = predictions
blocks['isOpen'] = np.where(blocks['prediction']>=0.95, 'yes', 'no')

for i in range(1, len(features)):
    tmpStreetName = features[i]['properties']['StreetName']
    tmpBetweenStreet1 = features[i]['properties']['BetweenStreet1']
    tmpBetweenStreet2 = features[i]['properties']['BetweenStreet2']
    tmpPrediction = blocks[(blocks['StreetName'] == tmpStreetName) & (blocks['BetweenStreet1'] == tmpBetweenStreet1) & (blocks['BetweenStreet2'] == tmpBetweenStreet2)]['prediction'].values[0]
    tmpIsOpen = blocks[(blocks['StreetName'] == tmpStreetName) & (blocks['BetweenStreet1'] == tmpBetweenStreet1) & (blocks['BetweenStreet2'] == tmpBetweenStreet2)]['isOpen'].values[0]

    features[i]['properties']['prediction'] = tmpPrediction
    features[i]['properties']['isOpen'] = tmpIsOpen

#return(features)


blocks


test = getBlockAvailability(features)
test
