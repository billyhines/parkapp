# import pandas as pd
# import numpy as np
# import datetime
# from dateutil.parser import parse
# from pymongo import MongoClient
# import itertools
#
# from flask import jsonify
# import geo_functions
# import cProfile
# from pymongo import MongoClient
#
# address = '818 Bourke St Melbourne Australia'
# time = '2019-11-28T22:20'
#
# client = MongoClient()
#
#
#
# address_data = []
# space_data = []
#
# user_point = geo_functions.geocode_address(address)
# closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150, client)
# type(closeBlocks)
#
#
# address_data.append({"type": "Feature",
#                         "geometry": {
#                             "type": "Point",
#                             "coordinates": user_point["coordinates"]},
#                         "properties": {
#                             "cleanAddress": user_point["address"]
#                     }})
#
# blockCoords = geo_functions.findBlockCoordinates(closeBlocks, client)
# space_data.extend(blockCoords)
# space_data = geo_functions.getBlockAvailability(space_data, time, client)
#
# timestamp = datetime.datetime.now()
#
# timestamp = datetime.datetime(2017, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
# type(timestamp)
