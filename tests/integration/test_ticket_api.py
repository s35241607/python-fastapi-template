from fastapi.testclient import TestClient

from app.models.enums import TicketStatus


def test_create_and_get_ticket(client: TestClient):
    """
    Tests creating a ticket and then retrieving it to ensure correctness.
    The `client` fixture handles database setup and authentication.
    """
    # Arrange: Define the payload for creating a new ticket
    ticket_data = {
        "title": "Integration Test Ticket",
        "description": "This is a test ticket created via the API.",
        "priority": "medium",
        "visibility": "internal",
        "category_ids": [],
        "label_ids": [],
    }

    # Act: Create the ticket
    response = client.post("/api/v1/tickets/", json=ticket_data)

    # Assert: Check if the creation was successful
    assert response.status_code == 201, response.text
    created_ticket = response.json()
    assert created_ticket["title"] == ticket_data["title"]
    assert created_ticket["status"] == TicketStatus.DRAFT.value
    ticket_id = created_ticket["id"]

    # Act: Fetch the ticket using the same authenticated client
    response = client.get(f"/api/v1/tickets/{ticket_id}")

    # Assert: Check if the fetch was successful and data is consistent
    assert response.status_code == 200, response.text
    fetched_ticket = response.json()
    assert fetched_ticket["id"] == ticket_id
    assert fetched_ticket["title"] == ticket_data["title"]