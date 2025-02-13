import pytest


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
