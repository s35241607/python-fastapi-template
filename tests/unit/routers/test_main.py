from fastapi.testclient import TestClient


def test_read_main(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI Ticket System"}


def test_read_tickets(client: TestClient):
    """Test the endpoint for reading tickets."""
    # The client fixture now handles authentication mocking.
    response = client.get("/api/v1/tickets/")

    # Assert
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)