import pytest


class TestGetAddress:
    @pytest.fixture(autouse=True)
    def prepare_IP(self, client):
        response = client.post("/address", json={"ip": "1.1.1.1"})

    def test_get_ip(self, client):
        response = client.get("/address/1.1.1.1")
        assert response.status_code == 200

    def test_get_ip_invalid_ip(self, client):
        response = client.get("/address/invalid")
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Invalid IP or URL address"}

    def test_get_ip_not_found(self, client):
        response = client.get("/address/2.2.2.2")
        assert response.status_code == 404
        assert response.get_json(force=True) == {"error": "IP or URL address not found"}

    def test_get_ip_redis_failure(self, client_with_failing_redis_exists):
        response = client_with_failing_redis_exists.get("/address/1.1.1.1")
        assert response.status_code == 500
