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

def test_findCloseMarker_ids_output1():
    # tests output of findCloseMarker_ids in the Eastern region of parking spaces

    expected_marker_ids = ['13228N','13230N','13232N','13233S','13234N','13235S','13236N','13237S','13238N','13239S',
                           '13240N','13242N','13244N','13246N','13248N','13250N','13252N','13254N','13256N','13612E',
                           '13614E','13616E','13617W','13618E','13619W','13620E','13621W','13622E','13623W','13624E',
                           '13625W','13626E','13627W','13628E','13630E','13632E','13634E','13637W','13639W','13641W',
                           '13644E','C13568','C13572','C13576','C13580','C13584','C13588','C13592','C13596','C13600',
                           'C13604','C13608','C13612','C13616','C13620','C13624','C13628','C13632','C13636','C13640',
                           'C13644','C13648','C13652','C13656','C13660','C13664','C13668','C13672','C13676','C13680']

    test_coords = [144.9440435, -37.8192278]
    test_meters = 100

    test_marker_ids = geo_functions.findCloseMarker_ids(test_coords, test_meters, client)
    assert expected_marker_ids == test_marker_ids


def test_findCloseMarker_ids_output2():
    # tests output of findCloseMarker_ids in the Western region of parking spaces

    expected_marker_ids = ['11700E','11701W','11702E','11703W','11704E','11705W','11707W','11708E',
                           '11709W','11710E','11712E','11714E','11716E','11718E','11720E','11722E',
                           '11724E','11726E','11730E','2493S','2495S','53W','55W','57W','59W','61W',
                           '63W','65W','67W','69W','71W','72E','73W','74E','75W','76E','77W','78E',
                           '79W','C2636','C2638']

    test_coords = [144.972554, -37.810075]
    test_meters = 100

    test_marker_ids = geo_functions.findCloseMarker_ids(test_coords, test_meters, client)
    assert expected_marker_ids == test_marker_ids

def test_findCloseMarker_ids_output3():
    # tests output of findCloseMarker_ids in the Northern region of parking spaces

    expected_marker_ids = ['6055W','6061W,6059','6221W','6223W','6225W','6227W','6229W','6231W','6233W',
                           '6235W','6237W','6239W','6241W','6243W','6245W','6288E','6292E','6294E','6306E',
                           '6310E','6313W','6314E','6315W','6318E','6322E','6326E','7592N','7594N','7595S',
                           '7596N','7597S','7599S','C6050','C6052','C6054','C6056','C6058','C6060','C6062',
                           'C6064','C6066','C6068','C6070','C6072','C6074','C6076','C6078','C6080','C6082',
                           'C6084','C6086','C6088','C6090','C6092','C6094','C6096','C6098','C6100','C6102',
                           'C6206','C6208','C6210','C6212','C6214','C6278','C6280','C6282','C6284','C6286',
                           'C6290','C6294','C6296','C6298','C6300','C6302','C6304']
    test_coords = [144.951398, -37.805313]
    test_meters = 100

    test_marker_ids = geo_functions.findCloseMarker_ids(test_coords, test_meters, client)
    assert expected_marker_ids == test_marker_ids

def test_findCloseMarker_ids_output4():
    # tests output of findCloseMarker_ids in the Southern region of parking spaces

    expected_marker_ids = ['10032N','10034N','10035S','10036N','10037S','10038N','10041S','10043S','10044N',
                           '10045S','10046N','10047S','10048N','8801W','8801W,8803','8803W','8805W','8808E',
                           '8810E','8812E','8814E,8816','8838E','8840E','8846E','8848E','8850E']

    test_coords = [144.966163, -37.823207]
    test_meters = 100

    test_marker_ids = geo_functions.findCloseMarker_ids(test_coords, test_meters, client)
    assert expected_marker_ids == test_marker_ids

def test_findCloseMarker_ids_zero_radius():
    # Tests using a radius of 0
    with pytest.raises(ValueError, match= "No parking bays found near specified point"):
        test_coords = [144.980629, -37.805379]
        test_meters = 0
        geo_functions.findCloseMarker_ids(test_coords, test_meters, client)

def test_findCloseMarker_ids_negative_radius():
    # Tests a negative radius
    with pytest.raises(OperationFailure):
        test_coords = [144.951398, -37.805313]
        test_meters = -100
        geo_functions.findCloseMarker_ids(test_coords, test_meters, client)

def test_findCloseMarker_ids_non_numeric_radius():
    # Tests a non-numeric radius
    with pytest.raises(OperationFailure):
        test_coords = [144.951398, -37.805313]
        test_meters = 'string'
        geo_functions.findCloseMarker_ids(test_coords, test_meters, client)

def test_findCloseMarker_ids_non_list_coords():
    # Tests a non-list set of coordinates
    with pytest.raises(TypeError, match= 'point must be a list of Long, Lat'):
        test_coords = "144.951398, -37.805313"
        test_meters = 100
        geo_functions.findCloseMarker_ids(test_coords, test_meters, client)

def test_findCloseMarker_ids_one_coors():
    # Tests a list witbh only a single coordinate
    with pytest.raises(ValueError, match= 'point must have a length of two'):
        test_coords = [144.951398]
        test_meters = 100
        geo_functions.findCloseMarker_ids(test_coords, test_meters, client)

def test_findCloseMarker_ids_out_of_range_coords():
    # Tests a non-numeric radius
    with pytest.raises(OperationFailure):
        test_coords = [14495139, -37805313]
        test_meters = 100
        geo_functions.findCloseMarker_ids(test_coords, test_meters, client)

def test_blocksFromMarker_ids_block_output1():
    # tests output of blocksFromMarker_ids in the Eastern region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['BOURKE STREET', 'BOURKE STREET', 'MERCHANT STREET',
                                                   'BOURKE STREET', 'IMPORT LANE', 'BOURKE STREET',
                                                   'ENTERPRIZE WAY', 'BOURKE STREET', 'MERCHANT STREET'],
                                    'BetweenStreet1': ['CAPTAIN WALK', 'MERCHANT STREET', 'BOURKE STREET',
                                                       'GEOGRAPHE STREET', 'COLLINS STREET', 'MERCHANT STREET',
                                                       'BOURKE STREET', 'ENTERPRIZE WAY', 'COLLINS STREET'],
                                    'BetweenStreet2': ['ENTERPRIZE WAY', 'SEAFARER LANE', 'VICTORIA HARBOUR PROMENADE',
                                                       'ENTERPRIZE WAY', 'BOURKE STREET', 'CUMBERLAND STREET',
                                                       'VICTORIA HARBOUR PROMENADE', 'MERCHANT STREET', 'BOURKE STREET']})

    test_markers = ['13228N','13230N','13232N','13233S','13234N','13235S','13236N','13237S','13238N','13239S',
                    '13240N','13242N','13244N','13246N','13248N','13250N','13252N','13254N','13256N','13612E',
                    '13614E','13616E','13617W','13618E','13619W','13620E','13621W','13622E','13623W','13624E',
                    '13625W','13626E','13627W','13628E','13630E','13632E','13634E','13637W','13639W','13641W',
                    '13644E','C13568','C13572','C13576','C13580','C13584','C13588','C13592','C13596','C13600',
                    'C13604','C13608','C13612','C13616','C13620','C13624','C13628','C13632','C13636','C13640',
                    'C13644','C13648','C13652','C13656','C13660','C13664','C13668','C13672','C13676','C13680']

    testing_blocks = geo_functions.blocksFromMarker_ids(test_markers, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)


def test_blocksFromMarker_ids_block_output2():
    # tests output of blocksFromMarker_ids in the Western region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['NICHOLSON STREET', 'SPRING STREET', 'LITTLE BOURKE STREET',
                                                   'SPRING STREET', 'LONSDALE STREET'],
                                    'BetweenStreet1': ['ALBERT STREET', 'LONSDALE STREET', 'EXHIBITION STREET',
                                                       'LITTLE BOURKE STREET', 'EXHIBITION STREET'],
                                    'BetweenStreet2': ['SPRING STREET', 'LITTLE BOURKE STREET', 'SPRING STREET',
                                                       'BOURKE STREET', 'SPRING STREET']})

    test_markers = ['11700E','11701W','11702E','11703W','11704E','11705W','11707W','11708E',
                    '11709W','11710E','11712E','11714E','11716E','11718E','11720E','11722E',
                    '11724E','11726E','11730E','2493S','2495S','53W','55W','57W','59W','61W',
                    '63W','65W','67W','69W','71W','72E','73W','74E','75W','76E','77W','78E',
                    '79W','C2636','C2638']

    testing_blocks = geo_functions.blocksFromMarker_ids(test_markers, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_blocksFromMarker_ids_block_output3():
    # tests output of blocksFromMarker_ids in the Northern region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['CHETWYND STREET', 'CHETWYND STREET', 'EADES PLACE',
                                                   'VICTORIA STREET', 'LEVESON STREET', 'VICTORIA STREET'],
                                    'BetweenStreet1': ['QUEENSBERRY STREET', 'VICTORIA STREET', 'VICTORIA STREET',
                                                       'ERROL STREET', 'QUEENSBERRY STREET', 'LEVESON STREET'],
                                    'BetweenStreet2': ['VICTORIA STREET', 'STANLEY STREET', 'STANLEY STREET',
                                                       'LEVESON STREET', 'VICTORIA STREET', 'CHETWYND STREET']})

    test_markers = ['6055W','6061W,6059','6221W','6223W','6225W','6227W','6229W','6231W','6233W',
                    '6235W','6237W','6239W','6241W','6243W','6245W','6288E','6292E','6294E','6306E',
                    '6310E','6313W','6314E','6315W','6318E','6322E','6326E','7592N','7594N','7595S',
                    '7596N','7597S','7599S','C6050','C6052','C6054','C6056','C6058','C6060','C6062',
                    'C6064','C6066','C6068','C6070','C6072','C6074','C6076','C6078','C6080','C6082',
                    'C6084','C6086','C6088','C6090','C6092','C6094','C6096','C6098','C6100','C6102',
                    'C6206','C6208','C6210','C6212','C6214','C6278','C6280','C6282','C6284','C6286',
                    'C6290','C6294','C6296','C6298','C6300','C6302','C6304']

    testing_blocks = geo_functions.blocksFromMarker_ids(test_markers, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_blocksFromMarker_ids_block_output4():
    # tests output of blocksFromMarker_ids in the Southern region of parking spaces
    expected_blocks = pd.DataFrame({'StreetName': ['FAWKNER STREET', 'KAVANAGH STREET', 'SOUTHBANK BOULEVARD',
                                                   'SOUTHBANK BOULEVARD', 'SOUTHBANK BOULEVARD'],
                                    'BetweenStreet1': ['SOUTHBANK BOULEVARD', 'SOUTHBANK BOULEVARD', 'STURT STREET',
                                                       'KAVANAGH STREET', 'MOORE STREET'],
                                    'BetweenStreet2': ['FANNING STREET', 'STURT STREET', 'KAVANAGH STREET',
                                                       'FAWKNER STREET', 'KAVANAGH STREET']})

    test_markers = ['10032N','10034N','10035S','10036N','10037S','10038N','10041S','10043S','10044N',
                    '10045S','10046N','10047S','10048N','8801W','8801W,8803','8803W','8805W','8808E',
                    '8810E','8812E','8814E,8816','8838E','8840E','8846E','8848E','8850E']

    testing_blocks = geo_functions.blocksFromMarker_ids(test_markers, client)
    testing_blocks.reset_index(inplace=True, drop = True)

    pd.testing.assert_frame_equal(expected_blocks, testing_blocks)

def test_blocksFromMarker_ids_no_markers():
    # tests sending an empty list to blocksFromMarker_ids
    with pytest.raises(ValueError, match= "No parking bays found near specified point"):
        test_markers = []
        geo_functions.blocksFromMarker_ids(test_markers, client)

def test_blocksFromMarker_ids_bad_markers():
    # tests sending an list of non-markerIds to blocksFromMarker_ids
    with pytest.raises(ValueError, match= "No parking bays found near specified point"):
        test_markers = ['frank', '5555']
        geo_functions.blocksFromMarker_ids(test_markers, client)
