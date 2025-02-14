class TestPostAddress:
    def test_add_ip(self, client):
        response = client.post("/address", json={"ip": "100.1.1.1"})
        assert response.status_code == 201
        assert b"100.1.1.1" in response.data

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
        assert response.get_json(force=True) == {"error": "No IP or URL provided"}

    def test_add_ip_invalid_ip(self, client):
        response = client.post("/address", json={"ip": "invalid"})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Invalid IP or URL address"}

    def test_add_ip_ip_exists(self, client):
        client.post("/address", json={"ip": "111.1.1.1"})
        response = client.post("/address", json={"ip": "111.1.1.1"})
        assert response.status_code == 400
        assert response.get_json(force=True) == {"error": "Address already exists"}

    def test_add_ip_invalid_address(self, client):
        response = client.post("/address", json={"address": "http://invalid"})
        assert response.status_code == 400

    def test_add_ip_valid_address(self, client):
        response = client.post("/address", json={"address": "http://www.valid.com/"})
        assert response.status_code == 201

    def test_add_ip_redis_failure(self, client_with_failing_redis_exists):
        response = client_with_failing_redis_exists.post(
            "/address", json={"ip": "1.1.1.1"}
        )
        assert response.status_code == 500
