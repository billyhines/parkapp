from flask import Flask, render_template, jsonify, request
import geo_functions
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient()
db = client['parking']
geodata_collection = db.bayData

@app.route("/address-point", methods=['POST'])
def get_user_point():
    address = request.get_json()['address']

    features = []
    user_point = geo_functions.geocode_address(address)
    features.append({   "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": user_point}})

    return jsonify(features)

@app.route("/nearby-parking", methods=['POST'])
def get_parking_data():
    #if request.method == "POST":
    address = request.get_json()['address']

    features = []
    user_point = geo_functions.geocode_address(address)
    closeBlocks = geo_functions.findCloseBlocks(user_point, 150)
    features.extend(closeBlocks)

    featuresWithPrediction = geo_functions.getBlockAvailability(features)

    return jsonify(featuresWithPrediction)

@app.route('/')
def main():
    return render_template('main.html')

app.run()
