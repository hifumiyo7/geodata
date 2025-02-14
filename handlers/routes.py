from flask import Flask, request, abort, Response
import json
import redis
import requests
from urllib.parse import urlparse
import validators
from utils.redis_utils import delete, keys, raise_function, get, exists, set


def configure_address_routes(app: Flask, redis_connection: redis.Redis):
    @raise_function
    @app.route("/address", methods=["POST"])
    def add_ip():
        if not (data := request.get_json(force=True)):
            return json.dumps({"error": "No data provided"}), 400
        if address := data.get("ip"):
            url = ""
            if not validators.ipv4(address):
                return json.dumps({"error": "Invalid IP or URL address"}), 400
        elif url := data.get("address"):
            address = urlparse(url).netloc
            if not validators.url(url):
                return json.dumps({"error": "Invalid URL address"}), 400
        else:
            return json.dumps({"error": "No IP or URL provided"}), 400
        if exists(redis_connection, address):
            return json.dumps({"error": "Address already exists"}), 400
        request_url = f"http://ip-api.com/json/{address}"
        try:
            response = requests.get(request_url)
            response_json = response.json()
            if response.status_code != 200:
                return (
                    json.dumps(
                        {
                            "error": "Error fetching data",
                            "error_information": response.json(),
                        }
                    ),
                    500,
                )
            if response_json.get("status") == "fail":
                return (
                    json.dumps(
                        {"error": "Invalid IP or URL address based on ip-api.com"}
                    ),
                    400,
                )
        except Exception as e:
            return json.dumps({"error": "Error fetching data"}), 500
        set(redis_connection, url or address, json.dumps(response_json))
        return json.dumps({address: response_json}), 201

    @raise_function
    @app.route("/address", methods=["GET"])
    def get_all_ip_with_data():
        all_keys = redis_connection.keys()
        all_data = {}
        for key in all_keys:
            all_data[key.decode()] = json.loads(get(redis_connection, key.decode()))
        return json.dumps(all_data), 200

    @raise_function
    @app.route("/address/adresses", methods=["GET"])
    def get_all_ip():
        all_keys = [str(element) for element in keys(redis_connection)]
        return json.dumps(all_keys), 200

    @raise_function
    @app.route("/address/<address>", methods=["GET"])
    def get_ip(address):
        if not validators.ipv4(address) and not validators.url(address):
            return json.dumps({"error": "Invalid IP or URL address"}), 400
        if not exists(redis_connection, address):
            return json.dumps({"error": "IP or URL address not found"}), 404
        return_information = get(redis_connection, address)
        try:
            return_information = json.loads(return_information)
        except Exception:
            return json.dumps({"error": "Invalid data"}), 500
        return json.dumps({address: return_information}), 200

    @raise_function
    @app.route("/address/<address>", methods=["DELETE"])
    def delete_ip(address):
        if not validators.ipv4(address) and not validators.url(address):
            return json.dumps({"error": "Invalid IP or URL address"}), 400
        if not exists(redis_connection, address):
            return json.dumps({"error": "IP or URL address not found"}), 404
        delete(redis_connection, address)
        return "", 204

    @raise_function
    @app.route("/address/<address>", methods=["PUT", "PATCH"])
    def put_patch_ip(address):
        if not validators.ipv4(address) and not validators.url(address):
            return json.dumps({"error": "Invalid IP or URL address"}), 400
        return_code = 200
        if not exists(redis_connection, address):
            if request.method == "PATCH":
                return json.dumps({"error": "IP or URL address not found"}), 404
            return_code = 201
        existing_data = {}
        if request.method == "PATCH":
            existing_data = json.loads(get(redis_connection, address))
        if not (data := request.get_json(force=True)):
            return json.dumps({"error": "No data in JSON format provided"}), 400
        try:
            existing_data.update(data)
            data_to_put = json.dumps(existing_data)
        except Exception:
            return json.dumps({"error": "Invalid data"}), 400
        set(redis_connection, address, data_to_put)
        return data, return_code
