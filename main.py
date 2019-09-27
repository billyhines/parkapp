from flask import Flask, render_template, jsonify, request
import geo_functions
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient()
db = client['parking']
geodata_collection = db.bayData

@app.route('/geojson-features', methods=['GET'])
def get_all_points():
    features = []
    for geo_feature in geodata_collection.find({}).limit(90):
        features.append({
            "type": "Feature",
            "geometry": {
                "type": geo_feature['geometry']['type'],
                "coordinates": geo_feature['geometry']['coordinates']
            }
        })
    return jsonify(features)

@app.route("/geojson-user", methods=['POST'])
def index():
    #if request.method == "POST":
    address = request.get_json()['address']

    features = []
    user_point = geo_functions.geocode_address(address)
    features.append({   "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": user_point}})

    return jsonify(features)


@app.route('/')
def main():
    return render_template('main.html')

app.run()
