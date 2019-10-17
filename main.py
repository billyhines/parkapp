from flask import Flask, render_template, jsonify, request
import geo_functions

app = Flask(__name__)

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
    address = request.get_json()['address']
    time = request.get_json()['time']

    features = []
    user_point = geo_functions.geocode_address(address)
    closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150)
    features.extend(closeBlocks)

    featuresWithPrediction = geo_functions.getBlockAvailability(features, time)

    return jsonify(featuresWithPrediction)

@app.route('/')
def main():
    return render_template('main.html')

app.run()
