import pytest
from fastapi.testclient import TestClient
from app.models.enums import TicketStatus, TicketVisibility

# Default user ID from the test fixture
CREATOR_USER_ID = 1
ASSIGNEE_USER_ID = 2
UNRELATED_USER_ID = 99

@pytest.mark.asyncio
async def test_create_and_get_ticket(client: TestClient):
    """
    Tests creating a public ticket and then retrieving it.
    """
    ticket_data = {
        "title": "Integration Test Ticket",
        "description": "This is a test ticket created via the API.",
        "priority": "medium",
        "visibility": "internal",
    }
    response = client.post("/api/v1/tickets/", json=ticket_data)
    assert response.status_code == 201
    created_ticket = response.json()
    ticket_id = created_ticket["id"]

    response = client.get(f"/api/v1/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["title"] == ticket_data["title"]


@pytest.mark.asyncio
async def test_ticket_permission_scenarios(get_client_for_user: callable):
    """
    Tests various permission scenarios for a restricted ticket, including:
    - Creator access
    - Unrelated user rejection
    - Assignee access and state changes
    - Creator state changes
    """
    from app.database import engine
    from app.models import ApprovalTemplate, ApprovalTemplateStep

    # 0. Setup: Create an approval template and step directly in the DB for this test
    async with engine.connect() as conn:
        # Create Template
        result = await conn.execute(
            ApprovalTemplate.__table__.insert().values(name="Test Template", created_by=CREATOR_USER_ID)
        )
        await conn.commit()
        template_id = result.lastrowid

        # Create Step for the template, making the assignee the approver
        await conn.execute(
            ApprovalTemplateStep.__table__.insert().values(
                approval_template_id=template_id,
                step_order=1,
                user_id=ASSIGNEE_USER_ID, # Assignee is the approver
                is_mandatory=True,
            )
        )
        await conn.commit()

    # 1. Creator creates a restricted ticket with an approval process
    creator_client = get_client_for_user(CREATOR_USER_ID)
    ticket_data = {
        "title": "Restricted Ticket",
        "description": "A test for permissions.",
        "visibility": TicketVisibility.RESTRICTED.value,
        "priority": "high",
        "approval_template_id": template_id,
    }
    response = creator_client.post("/api/v1/tickets/", json=ticket_data)
    assert response.status_code == 201
    ticket_id = response.json()["id"]

    # 2. Creator can read their own ticket
    response = creator_client.get(f"/api/v1/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Restricted Ticket"

    # 3. Unrelated user is denied access
    unrelated_client = get_client_for_user(UNRELATED_USER_ID)
    response = unrelated_client.get(f"/api/v1/tickets/{ticket_id}")
    assert response.status_code == 403

    # 4. Creator assigns the ticket to another user (who is also the approver)
    creator_client = get_client_for_user(CREATOR_USER_ID)
    update_payload = {"assigned_to": ASSIGNEE_USER_ID}
    response = creator_client.put(f"/api/v1/tickets/{ticket_id}", json=update_payload)
    assert response.status_code == 200, response.text
    assert response.json()["assigned_to"] == ASSIGNEE_USER_ID

    # 5. Assignee/Approver can now access the ticket
    assignee_client = get_client_for_user(ASSIGNEE_USER_ID)
    response = assignee_client.get(f"/api/v1/tickets/{ticket_id}")
    assert response.status_code == 200

    # --- Test Status Change Permissions ---

    # 6. Creator submits the ticket for approval
    creator_client = get_client_for_user(CREATOR_USER_ID)
    response = creator_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "waiting_approval"})
    assert response.status_code == 200
    assert response.json()["status"] == TicketStatus.WAITING_APPROVAL.value

    # 7. Creator CANNOT approve the ticket
    response = creator_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "open"})
    assert response.status_code == 403

    # 8. Assignee (as the designated approver) CAN approve the ticket, moving it to OPEN
    assignee_client = get_client_for_user(ASSIGNEE_USER_ID)
    response = assignee_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "open"})
    assert response.status_code == 200
    assert response.json()["status"] == TicketStatus.OPEN.value

    # 9. Creator (not assignee) CANNOT start progress
    creator_client = get_client_for_user(CREATOR_USER_ID)
    response = creator_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "in_progress"})
    assert response.status_code == 403

    # 10. Assignee CAN start progress
    assignee_client = get_client_for_user(ASSIGNEE_USER_ID)
    response = assignee_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["status"] == TicketStatus.IN_PROGRESS.value

    # 11. Assignee resolves the ticket
    response = assignee_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "resolved"})
    assert response.status_code == 200
    assert response.json()["status"] == TicketStatus.RESOLVED.value

    # 12. Assignee CANNOT close the ticket
    response = assignee_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "closed"})
    assert response.status_code == 403

    # 13. Creator CAN close the ticket
    creator_client = get_client_for_user(CREATOR_USER_ID)
    response = creator_client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "closed"})
    assert response.status_code == 200
    assert response.json()["status"] == TicketStatus.CLOSED.value