from flask import Flask
import pytest

from handlers.routes import configure_routes


@pytest.fixture
def app():
    app = Flask(__name__)
    configure_routes(app, None)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestRoutes:
    def test_hello_world(self, app: Flask):
        with app.test_client() as c:
            response = c.get("/hello")
            assert response.data == b"hello"
            assert response.status_code == 200

    def test_add_ip(self, client):
        response = client.post("/address", json={"ip": "1.1.1.1"})
        assert response.status_code == 201
