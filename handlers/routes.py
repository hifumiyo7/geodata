from flask import Flask, request, abort, Response
import json
import redis

from utils.ip_utils import isIP
from utils.redis_utils import delete, raise_function, get, exists, set


def configure_address_routes(app: Flask, redis_connection: redis.Redis):

    @app.route("/hello", methods=["GET"])
    def get_hello():
        return "hello"

    @raise_function
    @app.route("/address", methods=["POST"])
    def add_ip():
        if not (data := request.get_json(force=True)):
            return json.dumps({"error": "No data provided"}), 400
        if not (ip := data.get("ip")):
            return json.dumps({"error": "No IP provided"}), 400
        if not isIP(ip):
            return json.dumps({"error": "Invalid IP address"}), 400
        if exists(redis_connection, ip):
            return json.dumps({"error": "IP address already exists"}), 400
        location_data = {"location": "unknown", "ip": ip}
        set(redis_connection, ip, json.dumps(location_data))
        return json.dumps({ip: location_data}), 201

    @raise_function
    @app.route("/address/<ip>", methods=["GET"])
    def get_ip(ip):
        if not isIP(ip):
            return json.dumps({"error": "Invalid IP address"}), 400
        if not exists(redis_connection, ip):
            return json.dumps({"error": "IP address not found"}), 404
        return_information = get(redis_connection, ip)
        try:
            print(return_information)
            return_information = json.loads(return_information)
        except Exception:
            return json.dumps({"error": "Invalid data"}), 500
        return json.dumps({ip: return_information}), 200

    @raise_function
    @app.route("/address/<ip>", methods=["DELETE"])
    def delete_ip(ip):
        if not isIP(ip):
            return json.dumps({"error": "Invalid IP address"}), 400
        if not exists(redis_connection, ip):
            return json.dumps({"error": "IP address not found"}), 404
        delete(redis_connection, ip)
        return "", 204

    @raise_function
    @app.route("/address/<ip>", methods=["PUT"])
    def put_ip(ip):
        if not isIP(ip):
            return json.dumps({"error": "Invalid IP address"}), 400
        if not (data := request.get_json(force=True)):
            return json.dumps({"error": "No data in JSON format provided"}), 400
        try:
            data_to_put = json.dumps(data)
        except Exception:
            return json.dumps({"error": "Invalid data"}), 400
        set(redis_connection, ip, data_to_put)
        return json.dumps(data), 200
