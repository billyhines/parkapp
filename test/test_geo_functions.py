import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

from geo_functions import findCloseBlocks

import pytest
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import OperationFailure

client = MongoClient()

def test_block_output1():
    # tests output of findCloseBlocks in the Eastern region of parking spaces
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

def test_block_output2():
    # tests output of findCloseBlocks in the Western region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['NICHOLSON STREET', 'SPRING STREET', 'LITTLE BOURKE STREET',
                                                   'SPRING STREET', 'LONSDALE STREET'],
                                    'BetweenStreet1': ['ALBERT STREET', 'LONSDALE STREET', 'EXHIBITION STREET',
                                                       'LITTLE BOURKE STREET', 'EXHIBITION STREET'],
                                    'BetweenStreet2': ['SPRING STREET', 'LITTLE BOURKE STREET', 'SPRING STREET',
                                                       'BOURKE STREET', 'SPRING STREET']})
    test_coords = [144.972554, -37.810075]
    test_meters = 100
    testing_blocks = findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_block_output3():
    # tests output of findCloseBlocks in the Northern region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['CHETWYND STREET', 'CHETWYND STREET', 'EADES PLACE',
                                                   'VICTORIA STREET', 'LEVESON STREET', 'VICTORIA STREET'],
                                    'BetweenStreet1': ['QUEENSBERRY STREET', 'VICTORIA STREET', 'VICTORIA STREET',
                                                       'ERROL STREET', 'QUEENSBERRY STREET', 'LEVESON STREET'],
                                    'BetweenStreet2': ['VICTORIA STREET', 'STANLEY STREET', 'STANLEY STREET',
                                                       'LEVESON STREET', 'VICTORIA STREET', 'CHETWYND STREET']})
    test_coords = [144.951398, -37.805313]
    test_meters = 100
    testing_blocks = findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_block_output4():
    # tests output of findCloseBlocks in the Southern region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['FAWKNER STREET', 'KAVANAGH STREET', 'SOUTHBANK BOULEVARD',
                                                   'SOUTHBANK BOULEVARD', 'SOUTHBANK BOULEVARD'],
                                    'BetweenStreet1': ['SOUTHBANK BOULEVARD', 'SOUTHBANK BOULEVARD', 'STURT STREET',
                                                       'KAVANAGH STREET', 'MOORE STREET'],
                                    'BetweenStreet2': ['FANNING STREET', 'STURT STREET', 'KAVANAGH STREET',
                                                       'FAWKNER STREET', 'KAVANAGH STREET']})
    test_coords = [144.966163, -37.823207]
    test_meters = 100
    testing_blocks = findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_no_blocks():
    # Tests a point that does not have any blocks within it's radius
    with pytest.raises(ValueError, match= "No parking bays found near specified point"):
        test_coords = [144.980629, -37.805379]
        test_meters = 100
        findCloseBlocks(test_coords, test_meters, client)

def test_zero_radius():
    # Tests using a radius of 0
    with pytest.raises(ValueError, match= "No parking bays found near specified point"):
        test_coords = [144.980629, -37.805379]
        test_meters = 0
        findCloseBlocks(test_coords, test_meters, client)

def test_negative_radius():
    # Tests a negative radius
    with pytest.raises(OperationFailure):
        test_coords = [144.951398, -37.805313]
        test_meters = -100
        findCloseBlocks(test_coords, test_meters, client)
