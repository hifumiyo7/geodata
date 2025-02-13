from flask import Flask
import redis

from handlers.routes import configure_routes

app = Flask(__name__)
redis_connection = redis.Redis(host="redis", port=6379, db=0)


configure_routes(app, redis_connection)

if __name__ == "__main__":
    app.run()
