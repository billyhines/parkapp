import geo_functions
import cProfile
import pandas as pd
import datetime
from dateutil.parser import parse
from pymongo import MongoClient

#address = '252 Swanston St Melbourne Australia'
address = '818 Bourke St Melbourne Australia'
time = '2019-11-28T22:20'

features = []
user_point = geo_functions.geocode_address(address)
closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150)
features.extend(closeBlocks)


prof = cProfile.run("""

featuresWithPrediction = geo_functions.getBlockAvailability(features, time)

""", sort=2)
