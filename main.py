from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import geo_functions

app = Flask(__name__)
app.secret_key = 'super secret'

@app.route("/address-and-parking", methods=['POST'])
def get_address_and_parking():
    """Geocode address and find close parking. Return GeoJSON along with availablity for parking spaces.

    :param address: The address entered by the user.
    :type address: str
    :param time: The time entered by the user.
    :type time: str
    :returns:  GeoJSON -- the address and parking in a GeoJSON.
    """
    client = MongoClient()

    address = request.get_json()['address']
    time = request.get_json()['time']

    address_data = []
    space_data = []

    try:
        user_point = geo_functions.geocode_address(address)
        closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 200 , client)
    except ValueError as e:
        return jsonify({"message": e.message}), 400

    address_data.append({"type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": user_point["coordinates"]},
                            "properties": {
                                "cleanAddress": user_point["address"]
                        }})

    blockCoords = geo_functions.findBlockCoordinates(closeBlocks, client)
    space_data.extend(blockCoords)

    try:
        space_data = geo_functions.getBlockAvailability(space_data, time, client)
    except ValueError as e:
        return jsonify({"message": e.message}), 400

    mapping_data = {"address_data": address_data,
                    "space_data" : space_data}

    client.close()

    return jsonify(mapping_data)

@app.route('/')
def main():
    return render_template('main.html')
#app.run()
