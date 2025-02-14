from flask import Flask
import pytest
import fakeredis
import redis.exceptions

from handlers.routes import configure_address_routes


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("redis.Redis", fakeredis.FakeStrictRedis)
    mock_redis = fakeredis.FakeStrictRedis()
    app = Flask(__name__)
    configure_address_routes(app, mock_redis)
    return app.test_client()


class MockResponse:
    status_code = 200

    @staticmethod
    def json():
        return {"area": "new area"}


@pytest.fixture(autouse=True, scope="function")
def request_data(monkeypatch):

    monkeypatch.setattr("requests.get", lambda x: MockResponse())


@pytest.fixture
def client_with_failing_redis_exists(monkeypatch):
    def failing_set(*args, **kwargs):
        raise redis.exceptions.ConnectionError("Failed to set key")

    monkeypatch.setattr("redis.Redis.set", failing_set)

    def failing_get(*args, **kwargs):
        raise redis.exceptions.ConnectionError("Failed to get key")

    monkeypatch.setattr("redis.Redis.get", failing_get)

    def failing_delete(*args, **kwargs):
        raise redis.exceptions.ConnectionError("Failed to delete key")

    monkeypatch.setattr("redis.Redis.delete", failing_delete)

    def failing_exists(*args, **kwargs):
        raise redis.exceptions.ConnectionError("Failed to check if key exists")

    monkeypatch.setattr("redis.Redis.exists", failing_exists)

    mock_failing_redis = fakeredis.FakeStrictRedis()
    app = Flask(__name__)
    configure_address_routes(app, mock_failing_redis)
    return app.test_client()
