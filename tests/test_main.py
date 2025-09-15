from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI Template"}

def test_read_items():
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert response.json() == []
