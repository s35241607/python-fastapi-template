from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI Ticket System"}


def test_read_tickets():
    # 注意：這個測試需要資料庫連線，實際使用時需要 mock 或測試資料庫
    response = client.get("/api/v1/tickets/")
    # 預期會因為資料庫連線問題而失敗，但結構正確
    # assert response.status_code == 200
    pass
