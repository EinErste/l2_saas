import datetime as dt
import json
import dotenv
import os
import requests
from flask import Flask, jsonify, request

dotenv.load_dotenv()

MY_API_TOKEN = os.getenv("MY_API_TOKEN")
WEATHER_API_TOKEN = os.getenv("WEATHER_API_TOKEN")

app = Flask(__name__)


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
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/weather",
    methods=["POST"],
)
def weather_endpoint():
    json_data = request.get_json()

    validate_token(json_data.get("token"))

    location = json_data.get("location")
    date = json_data.get("date")

    result = {
        "requester_name": json_data.get("requester_name"),
        "timestamp": dt.datetime.now().isoformat(),
        "location": location,
        "date": date,
        "weather": get_weather(location, date)["forecast"]["forecastday"][0]["day"]
    }

    return result


def validate_token(token):
    if token is None:
        raise InvalidUsage("Token is required", status_code=400)
    if token != MY_API_TOKEN:
        raise InvalidUsage("Wrong API token", status_code=403)


def get_weather(location, date):
    url_base_url = "http://api.weatherapi.com/v1"
    url_api = "history.json"
    url = f"{url_base_url}/{url_api}"

    params = {
        "key": WEATHER_API_TOKEN,
        "q": location,
        "dt": date,
    }

    response = requests.get(url=url, params=params)
    print(response.url)
    return json.loads(response.text)
