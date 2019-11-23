from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import geo_functions

app = Flask(__name__)
app.secret_key = 'super secret'

@app.route("/address-point", methods=['POST'])
def get_user_point():
    address = request.get_json()['address']

    features = []
    user_point = geo_functions.geocode_address(address)

    features.append({"type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": user_point["coordinates"]},
                        "properties": {
                            "cleanAddress": user_point["address"]
                        }})

    return jsonify(features)

@app.route("/nearby-parking", methods=['POST'])
def get_parking_data():
    client = MongoClient()

    address = request.get_json()['address']
    time = request.get_json()['time']

    features = []

    try:
        user_point = geo_functions.geocode_address(address)
        closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150, client)
    except AttributeError as e:
        return jsonify({"message": e.message}), 400

    blockCoords = geo_functions.findBlockCoordinates(closeBlocks, client)
    features.extend(blockCoords)
    featuresWithPrediction = geo_functions.getBlockAvailability(features, time, client)

    client.close()

    return jsonify(featuresWithPrediction)

@app.route('/')
def main():
    return render_template('main.html')
#app.run()
