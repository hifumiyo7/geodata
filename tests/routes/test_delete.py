import pytest


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
