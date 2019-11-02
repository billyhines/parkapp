from flask import Flask, render_template, jsonify, request
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

    address = request.get_json()['address']
    time = request.get_json()['time']

    features = []

    try:
        user_point = geo_functions.geocode_address(address)
    except:
        raise InvalidUsage('Could not find address', status_code=404)

    try:
        closeBlocks = geo_functions.findCloseBlocks(user_point["coordinates"], 150)
    except:
        raise InvalidUsage('No parking found near address', status_code=404)

    features.extend(closeBlocks)
    featuresWithPrediction = geo_functions.getBlockAvailability(features, time)

    return jsonify(featuresWithPrediction)

@app.route('/')
def main():
    return render_template('main.html')


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

app.run()
