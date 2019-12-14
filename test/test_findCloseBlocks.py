import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
from geo_functions import findCloseBlocks

def test_answer():
    import pandas as pd
    from pymongo import MongoClient

    client = MongoClient()

    expected_blocks = pd.DataFrame({'StreetName': ['BOURKE STREET', 'BOURKE STREET', 'MERCHANT STREET',
                                                   'BOURKE STREET', 'IMPORT LANE', 'BOURKE STREET',
                                                   'ENTERPRIZE WAY', 'BOURKE STREET', 'MERCHANT STREET'],
                                    'BetweenStreet1': ['CAPTAIN WALK', 'MERCHANT STREET', 'BOURKE STREET',
                                                       'GEOGRAPHE STREET', 'COLLINS STREET', 'MERCHANT STREET',
                                                       'BOURKE STREET', 'ENTERPRIZE WAY', 'COLLINS STREET'],
                                    'BetweenStreet2': ['ENTERPRIZE WAY', 'SEAFARER LANE', 'VICTORIA HARBOUR PROMENADE',
                                                       'ENTERPRIZE WAY', 'BOURKE STREET', 'CUMBERLAND STREET',
                                                       'VICTORIA HARBOUR PROMENADE', 'MERCHANT STREET', 'BOURKE STREET']})
    test_coords = [144.9440435, -37.8192278]
    test_meters = 100
    testing_blocks = findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)
