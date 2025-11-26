from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_user():
    response = client.post(
        "/users/",
        json={
            "name": "testuser",
            "email": "syang2501@outlook.com",
            "password": "123.qwe",
            "mobile": "17649862173"
        }
    )
    assert response is not None
    assert response.status_code == 200
    assert response.json()["name"] == "testuser"
