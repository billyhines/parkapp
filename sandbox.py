from pymongo import MongoClient
import geo_functions




address = '818 Bourke St Melbourne Australia'
time = '2019-11-28T22:20'


client = MongoClient()

test_coords = [144.972554, -37.810075]
test_meters = 40
testing_blocks = geo_functions.findCloseBlocks(test_coords, test_meters, client)
testing_blocks.reset_index(inplace=True, drop = True)

testing_blocks


len(geo_functions.findBlockCoordinates(testing_blocks, client))

#adding for test
