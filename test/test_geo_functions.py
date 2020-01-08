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

def test_findBlockCoordinates_block_output1():
    # tests output of findBlockCoordinates in the Eastern region of parking spaces
    expected_coords = [{'geometry': {'coordinates': [[[[144.94487616688087, -37.81944440108992],
                          [144.94480094769727, -37.81946617619086],
                          [144.94479252120462, -37.819447891204724],
                          [144.94486774144596, -37.81942607737698],
                          [144.94487616688087, -37.81944440108992]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'CAPTAIN WALK',
                       'BetweenStreet2': 'ENTERPRIZE WAY',
                       'StreetName': 'BOURKE STREET',
                       'description': u'Bourke Street between Harbour Esplanade and Enterprize Way'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.94513433460475, -37.81936966419339],
                          [144.945065012307, -37.819389731923735],
                          [144.94505654716616, -37.8193713228205],
                          [144.94512587158323, -37.81935121908499],
                          [144.94513433460475, -37.81936966419339]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'CAPTAIN WALK',
                       'BetweenStreet2': 'ENTERPRIZE WAY',
                       'StreetName': 'BOURKE STREET',
                       'description': u'Bourke Street between Harbour Esplanade and Enterprize Way'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9449391161512, -37.81942617778212],
                          [144.94487616688087, -37.81944440108992],
                          [144.94486774144596, -37.81942607737698],
                          [144.9449306767157, -37.81940782589276],
                          [144.9449391161512, -37.81942617778212]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'CAPTAIN WALK',
                       'BetweenStreet2': 'ENTERPRIZE WAY',
                       'StreetName': 'BOURKE STREET',
                       'description': u'Bourke Street between Harbour Esplanade and Enterprize Way'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.945065012307, -37.819389731923735],
                          [144.9450020642314, -37.81940795532061],
                          [144.94499361195577, -37.81938957437392],
                          [144.94505654716616, -37.8193713228205],
                          [144.945065012307, -37.819389731923735]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'CAPTAIN WALK',
                       'BetweenStreet2': 'ENTERPRIZE WAY',
                       'StreetName': 'BOURKE STREET',
                       'description': u'Bourke Street between Harbour Esplanade and Enterprize Way'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.94477961108245, -37.819472353476606],
                          [144.94470492552324, -37.81949397381659],
                          [144.94469651945144, -37.81947573153546],
                          [144.9447711888866, -37.81945407757575],
                          [144.94477961108245, -37.819472353476606]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'CAPTAIN WALK',
                       'BetweenStreet2': 'ENTERPRIZE WAY',
                       'StreetName': 'BOURKE STREET',
                       'description': u'Bourke Street between Harbour Esplanade and Enterprize Way'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9450020642314, -37.81940795532061],
                          [144.9449391150157, -37.819426177762296],
                          [144.9449306767157, -37.81940782589276],
                          [144.94499361195577, -37.81938957437392],
                          [144.9450020642314, -37.81940795532061]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'CAPTAIN WALK',
                       'BetweenStreet2': 'ENTERPRIZE WAY',
                       'StreetName': 'BOURKE STREET',
                       'description': u'Bourke Street between Harbour Esplanade and Enterprize Way'},
                      'type': 'Feature'}]
    test_block = pd.DataFrame({'StreetName': ['BOURKE STREET'],
                               'BetweenStreet1': ['CAPTAIN WALK'],
                               'BetweenStreet2': ['ENTERPRIZE WAY']})
    test_coords = geo_functions.findBlockCoordinates(test_block, client)

    assert expected_coords == test_coords

def test_findBlockCoordinates_block_output2():
    # tests output of findBlockCoordinates in the Western region of parking spaces
    expected_coords = [{'geometry': {'coordinates': [[[[144.97296201044801, -37.810168699037675],
                          [144.97293598585574, -37.810167131774726],
                          [144.97294196666513, -37.81010955394902],
                          [144.97296925677907, -37.810111530501956],
                          [144.97296201044801, -37.810168699037675]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9730054100601, -37.809838099281244],
                          [144.97299790503266, -37.8098933907215],
                          [144.97297008973328, -37.809891058181925],
                          [144.9729784169199, -37.80983577548941],
                          [144.9730054100601, -37.809838099281244]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9729630634504, -37.81056853547334],
                          [144.97296854367585, -37.810633343381966],
                          [144.97294340575965, -37.81063515097288],
                          [144.97293702221512, -37.810570022013785],
                          [144.9729630634504, -37.81056853547334]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97299046663136, -37.80994819757279],
                          [144.97298337540516, -37.81000193889899],
                          [144.97295575545732, -37.80999985483876],
                          [144.97296234262234, -37.80994589666529],
                          [144.97299046663136, -37.80994819757279]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97298337540516, -37.81000193889899],
                          [144.97297695122862, -37.81005180672964],
                          [144.97294928034634, -37.810049756936834],
                          [144.97295575545732, -37.80999985483876],
                          [144.97298337540516, -37.81000193889899]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97296201044801, -37.810168699037675],
                          [144.97295621479503, -37.810232673006254],
                          [144.97292954062908, -37.81023192995134],
                          [144.97293598585574, -37.810167131774726],
                          [144.97296201044801, -37.810168699037675]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.972728965777, -37.81012669253288],
                          [144.97272093598164, -37.81018064567867],
                          [144.97269377247812, -37.81017786018779],
                          [144.97270193605897, -37.81012375074012],
                          [144.972728965777, -37.81012669253288]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97297695122862, -37.81005180672964],
                          [144.97296925677907, -37.810111530501956],
                          [144.97294196666513, -37.81010955394902],
                          [144.97294928034634, -37.810049756936834],
                          [144.97297695122862, -37.81005180672964]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97275303607267, -37.809965735740256],
                          [144.97274501525476, -37.8100192375539],
                          [144.97271815488781, -37.81001625181959],
                          [144.97272614087754, -37.80996331805152],
                          [144.97275303607267, -37.809965735740256]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97273698548625, -37.81007319070238],
                          [144.972728965777, -37.81012669253288],
                          [144.97270193605897, -37.81012375074012],
                          [144.9727099304889, -37.81007075854301],
                          [144.97273698548625, -37.81007319070238]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97295351977417, -37.81029038759963],
                          [144.97295448181754, -37.81034949077933],
                          [144.972928363192, -37.81034969811656],
                          [144.9729274065411, -37.81028994167586],
                          [144.97295351977417, -37.81029038759963]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97299790503266, -37.8098933907215],
                          [144.97299046663136, -37.80994819757279],
                          [144.97296234262234, -37.80994589666529],
                          [144.97297008973328, -37.809891058181925],
                          [144.97299790503266, -37.8098933907215]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97274501525476, -37.8100192375539],
                          [144.97273698548625, -37.81007319070238],
                          [144.9727099304889, -37.81007075854301],
                          [144.97271815488781, -37.81001625181959],
                          [144.97274501525476, -37.8100192375539]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97302816481817, -37.8096902895845],
                          [144.9730186991373, -37.80974836976634],
                          [144.97299102145917, -37.809745451132166],
                          [144.97300074424388, -37.809687398809174],
                          [144.97302816481817, -37.8096902895845]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97297005151748, -37.810651183818976],
                          [144.97297033558073, -37.810654544694636],
                          [144.97297760724723, -37.81071237047606],
                          [144.9729528697436, -37.81071519428048],
                          [144.972945334128, -37.81065310679065],
                          [144.97297005151748, -37.810651183818976]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.97295448181754, -37.81034949077933],
                          [144.97295598342603, -37.81040718118842],
                          [144.97292989095632, -37.810408134249975],
                          [144.972928363192, -37.81034969811656],
                          [144.97295448181754, -37.81034949077933]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'ALBERT STREET',
                       'BetweenStreet2': 'SPRING STREET',
                       'StreetName': 'NICHOLSON STREET',
                       'description': u'Nicholson Street between Spring Street and Albert Street'},
                      'type': 'Feature'}]

    test_block = pd.DataFrame({'StreetName': ['NICHOLSON STREET'],
                               'BetweenStreet1': ['ALBERT STREET'],
                               'BetweenStreet2': ['SPRING STREET']})
    test_coords = geo_functions.findBlockCoordinates(test_block, client)

    assert expected_coords == test_coords

def test_findBlockCoordinates_block_output3():
    # tests output of findBlockCoordinates in the Northern region of parking spaces
    expected_coords = [{'geometry': {'coordinates': [[[[144.95223192138005, -37.805151125654554],
                          [144.95223625274903, -37.80512721709101],
                          [144.9522976043261, -37.805133346768955],
                          [144.95229331828725, -37.80515725972793],
                          [144.95223192138005, -37.805151125654554]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95245673827355, -37.80423805544155],
                          [144.95245262532214, -37.804261216235105],
                          [144.9523911645771, -37.80425507573543],
                          [144.95239524415618, -37.80423213695435],
                          [144.95245673827355, -37.80423805544155]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95236630734084, -37.80439485922773],
                          [144.95237049862834, -37.8043712897653],
                          [144.95243207198257, -37.80437697533874],
                          [144.9524278742326, -37.8044006149829],
                          [144.95236630734084, -37.80439485922773]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95234389199265, -37.80452440275849],
                          [144.95234793656508, -37.80450166343256],
                          [144.9524093318138, -37.80450779741099],
                          [144.9524052940712, -37.80453053685799],
                          [144.95234389199265, -37.80452440275849]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95222786617106, -37.80517350702184],
                          [144.95223192138005, -37.805151125654554],
                          [144.95229331828725, -37.80515725972793],
                          [144.9522893061367, -37.80517964545096],
                          [144.95222786617106, -37.80517350702184]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95232194186974, -37.804647832685575],
                          [144.952326713934, -37.8046210020576],
                          [144.95238814212655, -37.80462713932451],
                          [144.9523833780058, -37.804653970994494],
                          [144.95232194186974, -37.804647832685575]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95243150163023, -37.80402510318436],
                          [144.95243569209953, -37.80400156164006],
                          [144.95249698906207, -37.804008278722506],
                          [144.9524927526155, -37.80403212857304],
                          [144.95243150163023, -37.80402510318436]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95233978262502, -37.80454751404417],
                          [144.95234389199265, -37.80452440275849],
                          [144.9524052940712, -37.80453053685799],
                          [144.9524011218025, -37.80455403455778],
                          [144.95233978262502, -37.80454751404417]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9523788219883, -37.80432448504734],
                          [144.9523830522596, -37.80430069637513],
                          [144.95244452550426, -37.80430683799793],
                          [144.95244030090353, -37.80433062767233],
                          [144.9523788219883, -37.80432448504734]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95229692436155, -37.80478851454061],
                          [144.95230106313883, -37.80476524426091],
                          [144.95236252997168, -37.80477138491785],
                          [144.95235839799983, -37.804794656219435],
                          [144.95229692436155, -37.80478851454061]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95232659266833, -37.80497161492217],
                          [144.95226555158536, -37.804965515892974],
                          [144.95226987618378, -37.804941645960085],
                          [144.9523308463861, -37.80494788433769],
                          [144.95232659266833, -37.80497161492217]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95231362502517, -37.80469460416623],
                          [144.95231780283356, -37.804671112875006],
                          [144.9523792435294, -37.80467725126557],
                          [144.95237507252662, -37.80470074357869],
                          [144.95231362502517, -37.80469460416623]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95245080843932, -37.803916639044864],
                          [144.95251213267736, -37.803923024059124],
                          [144.95250790565626, -37.803946820905146],
                          [144.95244658701898, -37.803940355781215],
                          [144.95245080843932, -37.803916639044864]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9522236168114, -37.80519695470793],
                          [144.95222786617106, -37.80517350702184],
                          [144.9522893061367, -37.80517964545096],
                          [144.95228506180376, -37.805203323026646],
                          [144.9522236168114, -37.80519695470793]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95230523846172, -37.804741761037825],
                          [144.95230930460872, -37.80471889952952],
                          [144.9523707589164, -37.80472503996397],
                          [144.95236669959937, -37.80474790159336],
                          [144.95230523846172, -37.804741761037825]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95230106313883, -37.80476524426091],
                          [144.95230523846172, -37.804741761037825],
                          [144.95236669959937, -37.80474790159336],
                          [144.95236252997168, -37.80477138491785],
                          [144.95230106313883, -37.80476524426091]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9524361944626, -37.80435375793808],
                          [144.95243207198257, -37.80437697533874],
                          [144.95237049862834, -37.8043712897653],
                          [144.95237461457094, -37.804348145248554],
                          [144.9524361944626, -37.80435375793808]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9525291267207, -37.80382735513682],
                          [144.95246785121907, -37.80382089437969],
                          [144.9524724409237, -37.80379511044021],
                          [144.9525337208892, -37.80380149106771],
                          [144.9525291267207, -37.80382735513682]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9522487049385, -37.805058497308295],
                          [144.95225303629536, -37.80503458874348],
                          [144.95231420996038, -37.80504070089933],
                          [144.95230992393354, -37.80506461385956],
                          [144.9522487049385, -37.805058497308295]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95228445930542, -37.804858608401226],
                          [144.95228864398035, -37.804835074875974],
                          [144.95235007627446, -37.80484152224029],
                          [144.9523459511146, -37.80486475220548],
                          [144.95228445930542, -37.804858608401226]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95229269402768, -37.804812303206276],
                          [144.95229692436155, -37.80478851454061],
                          [144.95235839799983, -37.804794656219435],
                          [144.95235417333654, -37.80481844588728],
                          [144.95229269402768, -37.804812303206276]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95231780283356, -37.804671112875006],
                          [144.95232194186974, -37.804647832685575],
                          [144.9523833780058, -37.804653970994494],
                          [144.9523792435294, -37.80467725126557],
                          [144.95231780283356, -37.804671112875006]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95233560745118, -37.80457099276611],
                          [144.95233978262502, -37.80454751404417],
                          [144.9524011218025, -37.80455403455778],
                          [144.95239702200527, -37.80457712888961],
                          [144.95233560745118, -37.80457099276611]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95254277328635, -37.80375053107023],
                          [144.95248152504237, -37.80374407259715],
                          [144.95248562125678, -37.80372106380807],
                          [144.95254687510203, -37.803727442171564],
                          [144.95254277328635, -37.80375053107023]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95230930460872, -37.80471889952952],
                          [144.95231362502517, -37.80469460416623],
                          [144.95237507252662, -37.80470074357869],
                          [144.9523707589164, -37.80472503996397],
                          [144.95230930460872, -37.80471889952952]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95238709035718, -37.80427798487067],
                          [144.9523911645771, -37.80425507573543],
                          [144.95245262532214, -37.804261216235105],
                          [144.9524485579073, -37.804284126392155],
                          [144.95238709035718, -37.80427798487067]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95240312914757, -37.80418779653571],
                          [144.95240730422321, -37.80416431961018],
                          [144.95246873996942, -37.8041704578636],
                          [144.95246457172416, -37.80419393491028],
                          [144.95240312914757, -37.80418779653571]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95228864398035, -37.804835074875974],
                          [144.95229269402768, -37.804812303206276],
                          [144.95235417333654, -37.80481844588728],
                          [144.95235007627446, -37.80484152224029],
                          [144.95228864398035, -37.804835074875974]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.952550963622, -37.803704423333194],
                          [144.95248966785195, -37.80369832991577],
                          [144.95249382338991, -37.80367498241441],
                          [144.95255518129707, -37.80368067588662],
                          [144.952550963622, -37.803704423333194]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95251602344345, -37.803901121044746],
                          [144.95245485777684, -37.803893888981186],
                          [144.95245908188465, -37.803870156971065],
                          [144.95252037553993, -37.80387661985116],
                          [144.95251602344345, -37.803901121044746]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95237461457094, -37.804348145248554],
                          [144.9523788219883, -37.80432448504734],
                          [144.95244030090353, -37.80433062767233],
                          [144.9524361944626, -37.80435375793808],
                          [144.95237461457094, -37.804348145248554]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.952326713934, -37.8046210020576],
                          [144.95233138794407, -37.80459471944137],
                          [144.95239280816867, -37.80460085656704],
                          [144.95238814212655, -37.80462713932451],
                          [144.952326713934, -37.8046210020576]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95239524415618, -37.80423213695435],
                          [144.95239905073413, -37.80421073443638],
                          [144.95246049900544, -37.8042168729123],
                          [144.95245673827355, -37.80423805544155],
                          [144.95239524415618, -37.80423213695435]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9525337208892, -37.80380149106771],
                          [144.9524724409237, -37.80379511044021],
                          [144.95247721347747, -37.80376829873468],
                          [144.95253853422938, -37.803774394395916],
                          [144.9525337208892, -37.80380149106771]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9523830522596, -37.80430069637513],
                          [144.95238709035718, -37.80427798487067],
                          [144.9524485579073, -37.804284126392155],
                          [144.95244452550426, -37.80430683799793],
                          [144.9523830522596, -37.80430069637513]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95223625274903, -37.80512721709101],
                          [144.95224035737172, -37.80510456803222],
                          [144.95230166475497, -37.805110693334626],
                          [144.9522976043261, -37.805133346768955],
                          [144.95223625274903, -37.80512721709101]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95242728155512, -37.8040488118323],
                          [144.95243150163023, -37.80402510318436],
                          [144.9524927526155, -37.80403212857304],
                          [144.9524885940758, -37.80405554270769],
                          [144.95242728155512, -37.8040488118323]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95250251388043, -37.803977176982755],
                          [144.95244132098185, -37.80396994173451],
                          [144.95244658701898, -37.803940355781215],
                          [144.95250790565626, -37.803946820905146],
                          [144.95250251388043, -37.803977176982755]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95252037553993, -37.80387661985116],
                          [144.95245908188465, -37.803870156971065],
                          [144.9524630679587, -37.80384776447481],
                          [144.95252436835102, -37.803854147265156],
                          [144.95252037553993, -37.80387661985116]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95225713977123, -37.80501193966372],
                          [144.95226147638454, -37.80498800505568],
                          [144.95232256168597, -37.804994107559615],
                          [144.9523182703778, -37.805018047463804],
                          [144.95225713977123, -37.80501193966372]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95224035737172, -37.80510456803222],
                          [144.9522446486057, -37.80508087865704],
                          [144.9523059117943, -37.8050869995838],
                          [144.95230166475497, -37.805110693334626],
                          [144.95224035737172, -37.80510456803222]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95248152504237, -37.80374407259715],
                          [144.95254277328635, -37.80375053107023],
                          [144.95253853422938, -37.803774394395916],
                          [144.95247721347747, -37.80376829873468],
                          [144.95248152504237, -37.80374407259715]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95234793656508, -37.80450166343256],
                          [144.9523520391809, -37.80447859077953],
                          [144.95241342875966, -37.80448472375586],
                          [144.9524093318138, -37.80450779741099],
                          [144.95234793656508, -37.80450166343256]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95225303629536, -37.80503458874348],
                          [144.95225713977123, -37.80501193966372],
                          [144.9523182703778, -37.805018047463804],
                          [144.95231420996038, -37.80504070089933],
                          [144.95225303629536, -37.80503458874348]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95226147638454, -37.80498800505568],
                          [144.95226555158536, -37.804965515892974],
                          [144.95232659266833, -37.80497161492217],
                          [144.95232256168597, -37.804994107559615],
                          [144.95226147638454, -37.80498800505568]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9522446486057, -37.80508087865704],
                          [144.9522487049385, -37.805058497308295],
                          [144.95230992393354, -37.80506461385956],
                          [144.9523059117943, -37.8050869995838],
                          [144.9522446486057, -37.80508087865704]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95239905073413, -37.80421073443638],
                          [144.95240312914757, -37.80418779653571],
                          [144.95246457172416, -37.80419393491028],
                          [144.95246049900544, -37.8042168729123],
                          [144.95239905073413, -37.80421073443638]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95249698906207, -37.804008278722506],
                          [144.95243569209953, -37.80400156164006],
                          [144.95244132098185, -37.80396994173451],
                          [144.95250251388043, -37.803977176982755],
                          [144.95249698906207, -37.804008278722506]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95251213267736, -37.803923024059124],
                          [144.95245080843932, -37.803916639044864],
                          [144.95245485777684, -37.803893888981186],
                          [144.95251602344345, -37.803901121044746],
                          [144.95251213267736, -37.803923024059124]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95233138794407, -37.80459471944137],
                          [144.95233560745118, -37.80457099276611],
                          [144.95239702200527, -37.80457712888961],
                          [144.95239280816867, -37.80460085656704],
                          [144.95233138794407, -37.80459471944137]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.95254687510203, -37.803727442171564],
                          [144.95248562125678, -37.80372106380807],
                          [144.95248966785195, -37.80369832991577],
                          [144.952550963622, -37.803704423333194],
                          [144.95254687510203, -37.803727442171564]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'QUEENSBERRY STREET',
                       'BetweenStreet2': 'VICTORIA STREET',
                       'StreetName': 'CHETWYND STREET',
                       'description': u'Chetwynd Street between Victoria Street and Queensberry Street'},
                      'type': 'Feature'}]

    test_block = pd.DataFrame({'StreetName': ['CHETWYND STREET'],
                               'BetweenStreet1': ['QUEENSBERRY STREET'],
                               'BetweenStreet2': ['VICTORIA STREET']})
    test_coords = geo_functions.findBlockCoordinates(test_block, client)

    assert expected_coords == test_coords

def test_findBlockCoordinates_block_output4():
    # tests output of findBlockCoordinates in the Southern region of parking spaces
    expected_coords = [{'geometry': {'coordinates': [[[[144.96581498926219, -37.822537212307225],
                          [144.96582703180349, -37.822553467590616],
                          [144.96577719566343, -37.82257630386511],
                          [144.96576555548947, -37.8225598761948],
                          [144.96581498926219, -37.822537212307225]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'SOUTHBANK BOULEVARD',
                       'BetweenStreet2': 'FANNING STREET',
                       'StreetName': 'FAWKNER STREET',
                       'description': u'Fawkner Street between Southbank Boulevard and Fanning Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.96561864975962, -37.82262486479727],
                          [144.96566441465134, -37.822604373396004],
                          [144.96567657531676, -37.82262058747897],
                          [144.96563000872834, -37.82264106503264],
                          [144.96561864975962, -37.82262486479727]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'SOUTHBANK BOULEVARD',
                       'BetweenStreet2': 'FANNING STREET',
                       'StreetName': 'FAWKNER STREET',
                       'description': u'Fawkner Street between Southbank Boulevard and Fanning Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.96581498926219, -37.822537212307225],
                          [144.96586540785984, -37.82251409770299],
                          [144.9658776387885, -37.8225302778338],
                          [144.96582703180349, -37.822553467590616],
                          [144.96581498926219, -37.822537212307225]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'SOUTHBANK BOULEVARD',
                       'BetweenStreet2': 'FANNING STREET',
                       'StreetName': 'FAWKNER STREET',
                       'description': u'Fawkner Street between Southbank Boulevard and Fanning Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.9659465949692, -37.82247686423034],
                          [144.96599751456873, -37.82245445032607],
                          [144.966009387618, -37.82247079728661],
                          [144.96595827859434, -37.82249328272098],
                          [144.9659465949692, -37.82247686423034]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'SOUTHBANK BOULEVARD',
                       'BetweenStreet2': 'FANNING STREET',
                       'StreetName': 'FAWKNER STREET',
                       'description': u'Fawkner Street between Southbank Boulevard and Fanning Street'},
                      'type': 'Feature'},
                     {'geometry': {'coordinates': [[[[144.96561864975962, -37.82262486479727],
                          [144.96563000872834, -37.82264106503264],
                          [144.9655851863222, -37.822660744525365],
                          [144.9655733265811, -37.82264511508846],
                          [144.96561864975962, -37.82262486479727]]]],
                       'type': 'MultiPolygon'},
                      'properties': {'BetweenStreet1': 'SOUTHBANK BOULEVARD',
                       'BetweenStreet2': 'FANNING STREET',
                       'StreetName': 'FAWKNER STREET',
                       'description': u'Fawkner Street between Southbank Boulevard and Fanning Street'},
                      'type': 'Feature'}]

    test_block = pd.DataFrame({'StreetName': ['FAWKNER STREET'],
                               'BetweenStreet1': ['SOUTHBANK BOULEVARD'],
                               'BetweenStreet2': ['FANNING STREET']})
    test_coords = geo_functions.findBlockCoordinates(test_block, client)

    assert expected_coords == test_coords
