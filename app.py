from flask import Flask
import redis

from handlers.routes import configure_address_routes

import json
import redis


def add_to_redis(redis_connection: redis.Redis):
    with open("data_dump.json", "r") as file:
        data = json.load(file)
    for key, value in data.items():
        redis_connection.set(key, json.dumps(value))
    return True


app = Flask(__name__)
redis_connection = redis.Redis(host="redis", port=6379, db=0)

add_to_redis(redis_connection)

configure_address_routes(app, redis_connection)

if __name__ == "__main__":
    app.run()
