import pandas as pd
import datetime
from dateutil.parser import parse
from pymongo import MongoClient

import geo_functions
import cProfile


#address = '252 Swanston St Melbourne Australia'
address = '818 Bourke St Melbourne Australia'
time = '2019-11-28T22:20'

features = []
user_point = geo_functions.geocode_address(address)
closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150)
features.extend(closeBlocks)
featuresWithPrediction = geo_functions.getBlockAvailability(features, time)

prof = cProfile.run("""
""", sort=2)


# Can't geolocate
address = 'trashjinput_wontlocat'
user_point = geo_functions.geocode_address(address)

# Can't find close blocks

address = '101 Arch Street Boston, MA'
user_point = geo_functions.geocode_address(address)
closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150)
