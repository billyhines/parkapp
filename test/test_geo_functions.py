import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

import geo_functions

import pytest
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import OperationFailure

client = MongoClient()

def test_geocode_address_output_address():
    # tests the geocoder to generate a clean address
    expected_address = 'Little Collins Street, Melbourne City, City of Melbourne, Victoria, 3000, Australia'

    test_query = '427 Little Collins St Melbourne Australia'
    test_geocode = geo_functions.geocode_address(test_query)
    test_address = test_geocode['address']

    assert test_address == expected_address

def test_geocode_address_output_coordinates():
    # tests the geocoder to generate a Lat Long
    expected_coordinates = [144.9640455, -37.8151106]

    test_query = '427 Little Collins St Melbourne Australia'
    test_geocode = geo_functions.geocode_address(test_query)
    test_coordinates = test_geocode['coordinates']

    assert test_coordinates == expected_coordinates

def test_geocode_address_bad_address():
    # Tests a non-address query
    with pytest.raises(ValueError, match= "Address could not be geocoded"):
        test_query = 'This should be a un-geocodable query'
        geo_functions.geocode_address(test_query)

def test_findCloseBlocks_block_output1():
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
    testing_blocks = geo_functions.findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_findCloseBlocks_block_output2():
    # tests output of findCloseBlocks in the Western region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['NICHOLSON STREET', 'SPRING STREET', 'LITTLE BOURKE STREET',
                                                   'SPRING STREET', 'LONSDALE STREET'],
                                    'BetweenStreet1': ['ALBERT STREET', 'LONSDALE STREET', 'EXHIBITION STREET',
                                                       'LITTLE BOURKE STREET', 'EXHIBITION STREET'],
                                    'BetweenStreet2': ['SPRING STREET', 'LITTLE BOURKE STREET', 'SPRING STREET',
                                                       'BOURKE STREET', 'SPRING STREET']})
    test_coords = [144.972554, -37.810075]
    test_meters = 100
    testing_blocks = geo_functions.findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_findCloseBlocks_block_output3():
    # tests output of findCloseBlocks in the Northern region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['CHETWYND STREET', 'CHETWYND STREET', 'EADES PLACE',
                                                   'VICTORIA STREET', 'LEVESON STREET', 'VICTORIA STREET'],
                                    'BetweenStreet1': ['QUEENSBERRY STREET', 'VICTORIA STREET', 'VICTORIA STREET',
                                                       'ERROL STREET', 'QUEENSBERRY STREET', 'LEVESON STREET'],
                                    'BetweenStreet2': ['VICTORIA STREET', 'STANLEY STREET', 'STANLEY STREET',
                                                       'LEVESON STREET', 'VICTORIA STREET', 'CHETWYND STREET']})
    test_coords = [144.951398, -37.805313]
    test_meters = 100
    testing_blocks = geo_functions.findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_findCloseBlocks_block_output4():
    # tests output of findCloseBlocks in the Southern region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['FAWKNER STREET', 'KAVANAGH STREET', 'SOUTHBANK BOULEVARD',
                                                   'SOUTHBANK BOULEVARD', 'SOUTHBANK BOULEVARD'],
                                    'BetweenStreet1': ['SOUTHBANK BOULEVARD', 'SOUTHBANK BOULEVARD', 'STURT STREET',
                                                       'KAVANAGH STREET', 'MOORE STREET'],
                                    'BetweenStreet2': ['FANNING STREET', 'STURT STREET', 'KAVANAGH STREET',
                                                       'FAWKNER STREET', 'KAVANAGH STREET']})
    test_coords = [144.966163, -37.823207]
    test_meters = 100
    testing_blocks = geo_functions.findCloseBlocks(test_coords, test_meters, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_findCloseBlocks_no_blocks():
    # Tests a point that does not have any blocks within it's radius
    with pytest.raises(ValueError, match= "No parking bays found near specified point"):
        test_coords = [144.980629, -37.805379]
        test_meters = 100
        geo_functions.findCloseBlocks(test_coords, test_meters, client)

def test_findCloseBlocks_zero_radius():
    # Tests using a radius of 0
    with pytest.raises(ValueError, match= "No parking bays found near specified point"):
        test_coords = [144.980629, -37.805379]
        test_meters = 0
        geo_functions.findCloseBlocks(test_coords, test_meters, client)

def test_findCloseBlocks_negative_radius():
    # Tests a negative radius
    with pytest.raises(OperationFailure):
        test_coords = [144.951398, -37.805313]
        test_meters = -100
        geo_functions.findCloseBlocks(test_coords, test_meters, client)

def test_findCloseBlocks_non_numeric_radius():
    # Tests a non-numeric radius
    with pytest.raises(OperationFailure):
        test_coords = [144.951398, -37.805313]
        test_meters = 'string'
        geo_functions.findCloseBlocks(test_coords, test_meters, client)


def test_findCloseBlocks_non_list_coords():
    # Tests a non-list set of coordinates
    with pytest.raises(TypeError, match= 'point must be a list of Long, Lat'):
        test_coords = "144.951398, -37.805313"
        test_meters = 100
        geo_functions.findCloseBlocks(test_coords, test_meters, client)

def test_findCloseBlocks_one_coors():
    # Tests a list witbh only a single coordinate
    with pytest.raises(ValueError, match= 'point must have a length of two'):
        test_coords = [144.951398]
        test_meters = 100
        geo_functions.findCloseBlocks(test_coords, test_meters, client)

def test_findCloseBlocks_out_of_range_coords():
    # Tests a non-numeric radius
    with pytest.raises(OperationFailure):
        test_coords = [14495139, -37805313]
        test_meters = 100
        geo_functions.findCloseBlocks(test_coords, test_meters, client)

def test_findCloseBlocks_bad_client():
    # Tests a bad mongo client passed in
    with pytest.raises(ValueError, match= 'client must be a MongoClient object'):
        test_coords = [144.972554, -37.810075]
        test_meters = 100
        test_client = 100
        geo_functions.findCloseBlocks(test_coords, test_meters, test_client)
