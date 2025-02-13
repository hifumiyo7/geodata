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


class TestPostAddress:
    def test_hello_world(self, client):
        response = client.get("/hello")
        assert response.data == b"hello"
        assert response.json is None
        assert response.status_code == 200

    def test_add_ip(self, client):
        response = client.post("/address", json={"ip": "1.1.1.1"})
        assert response.status_code == 201
        assert b"1.1.1.1" in response.data

    def test_add_ip_empty_data(self, client):
        response = client.post("/address", json=None, content_type="application/json")
        assert response.status_code == 400

    def test_add_ip_no_data(self, client):
        response = client.post("/address", json={})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "No data provided"}

    def test_add_ip_no_ip(self, client):
        response = client.post("/address", json={"a": "b"})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "No IP provided"}

    def test_add_ip_invalid_ip(self, client):
        response = client.post("/address", json={"ip": "invalid"})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Invalid IP address"}

    def test_add_ip_ip_exists(self, client):
        client.post("/address", json={"ip": "1.1.1.1"})
        response = client.post("/address", json={"ip": "1.1.1.1"})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "IP address already exists"}

    def test_add_ip_redis_failure(self, client_with_failing_redis_exists):
        response = client_with_failing_redis_exists.post(
            "/address", json={"ip": "1.1.1.1"}
        )
        assert response.status_code == 500


class TestGetAddress:
    @pytest.fixture(autouse=True)
    def prepare_IP(self, client):
        client.post("/address", json={"ip": "1.1.1.1"})

    def test_get_ip(self, client):
        response = client.get("/address/1.1.1.1")
        print(response.data)
        assert response.status_code == 200

    def test_get_ip_invalid_ip(self, client):
        response = client.get("/address/invalid")
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Invalid IP address"}

    def test_get_ip_not_found(self, client):
        response = client.get("/address/2.2.2.2")
        assert response.status_code == 404
        assert response.get_json(force=True) == {"error": "IP address not found"}

    def test_get_ip_redis_failure(self, client_with_failing_redis_exists):
        response = client_with_failing_redis_exists.get("/address/1.1.1.1")
        assert response.status_code == 500


class TestDeleteAddress:
    @pytest.fixture(autouse=True)
    def prepare_IP(self, client):
        client.post("/address", json={"ip": "1.1.1.1"})

    def test_delete_ip(self, client):
        response = client.delete("/address/1.1.1.1")
        assert response.status_code == 204

    def test_delete_ip_not_flaky(self, client):
        response = client.delete("/address/1.1.1.1")
        assert response.status_code == 204

    def test_delete_ip_invalid_ip(self, client):
        response = client.delete("/address/invalid")
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Invalid IP address"}

    def test_delete_ip_not_found(self, client):
        response = client.delete("/address/2.2.2.2")
        assert response.status_code == 404
        assert response.get_json(force=True) == {"error": "IP address not found"}

    def test_delete_ip_redis_failure(self, client_with_failing_redis_exists):
        response = client_with_failing_redis_exists.delete("/address/1.1.1.1")
        assert response.status_code == 500


class TestPutAddress:
    @pytest.fixture(autouse=True)
    def prepare_IP(self, client):
        client.post("/address", json={"ip": "1.1.1.1"})

    def test_put_ip(self, client):
        response = client.put("/address/1.1.1.1", json={"area": "new area"})
        assert response.status_code == 200
        assert response.get_json(force=True) == {"area": "new area"}

    def test_put_ip_changes_info(self, client):
        client.put("/address/1.1.1.1", json={"area": "new area"})
        response = client.get("/address/1.1.1.1")
        assert response.status_code == 200
        assert response.get_json(force=True) == {"1.1.1.1": {"area": "new area"}}

    def test_patch_ip_new_ip(self, client):
        response = client.put("/address/2.2.2.2", json={"area": "new area"})
        assert response.status_code == 201

    def test_put_ip_invalid_ip(self, client):
        response = client.put("/address/invalid", json={"area": "new area"})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Invalid IP address"}

    def test_put_ip_no_data(self, client):
        response = client.put("/address/1.1.1.1", json={})
        assert response.status_code == 400

    def test_put_ip_redis_failure(self, client_with_failing_redis_exists):
        response = client_with_failing_redis_exists.put(
            "/address/1.1.1.1", json={"area": "new area"}
        )
        assert response.status_code == 500


class TestPatchAddress:
    @pytest.fixture(autouse=True)
    def prepare_IP(self, client):
        client.post("/address", json={"ip": "1.1.1.1"})

    def test_patch_ip(self, client):
        response = client.patch("/address/1.1.1.1", json={"area": "new area"})
        assert response.status_code == 200
        assert response.get_json(force=True) == {"area": "new area"}

    def test_patch_ip_changes_info(self, client):
        client.patch("/address/1.1.1.1", json={"area": "new area"})
        response = client.get("/address/1.1.1.1")
        assert response.status_code == 200
        assert response.get_json(force=True) == {"1.1.1.1": {"area": "new area"}}

    def test_patch_ip_new_ip(self, client):
        response = client.patch("/address/2.2.2.2", json={"area": "new area"})
        assert response.status_code == 404
        assert response.get_json(force=True) == {"error": "IP address not found"}

    def test_patch_ip_invalid_ip(self, client):
        response = client.patch("/address/invalid", json={"area": "new area"})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Invalid IP address"}

    def test_put_ip_no_data(self, client):
        response = client.patch("/address/1.1.1.1", json={})
        assert response.status_code == 400

    def test_patch_ip_redis_failure(self, client_with_failing_redis_exists):
        response = client_with_failing_redis_exists.patch(
            "/address/1.1.1.1", json={"area": "new area"}
        )
        assert response.status_code == 500
