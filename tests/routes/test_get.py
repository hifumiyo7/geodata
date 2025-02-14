import pytest


class TestGetAddress:
    @pytest.fixture(autouse=True)
    def prepare_IP(self, client):
        response = client.post("/address", json={"ip": "1.1.1.1"})

    def test_get_adress(self, client):
        response = client.get("/address")
        assert response.status_code == 200

    def test_get_adress_adresses(self, client):
        response = client.get("/address/adresses")
        assert response.status_code == 200
