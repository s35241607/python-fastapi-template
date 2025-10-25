"""
Ticket 路由層單元測試

測試 ticket_router 中的端點，使用 mocked services。
"""

from datetime import datetime
from unittest.mock import patch

from fastapi import HTTPException, status

from app.models.enums import TicketPriority, TicketStatus, TicketVisibility
from app.schemas.response import PaginationResponse
from app.schemas.ticket import TicketRead


class TestTicketRouterCreate:
    """建立工單端點測試"""

    def test_create_ticket_success(self, client, auth_headers):
        """測試成功建立工單"""
        with patch("app.services.ticket_service.TicketService.create_ticket") as mock_create:
            mock_create.return_value = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Test Ticket",
                description="Test Description",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
                categories=[],
                labels=[],
            )

            payload = {
                "title": "Test Ticket",
                "description": "Test Description",
                "priority": "medium",
                "visibility": "internal",
                "category_ids": [],
                "label_ids": [],
            }

            response = client.post(
                "/api/v1/tickets/",
                json=payload,
                headers=auth_headers(),
            )

            assert response.status_code == 201
            assert response.json()["ticket_no"] == "TIC-20250101-001"

    def test_create_ticket_missing_title(self, client, auth_headers):
        """測試建立工單（缺少必填欄位 title）"""
        payload = {
            "description": "Test Description",
            # 缺少 title
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(),
        )

        assert response.status_code == 422

    def test_create_ticket_unauthorized(self, client):
        """測試未認證使用者建立工單"""
        payload = {
            "title": "Test Ticket",
            "description": "Test Description",
        }

        # 不提供認證頭
        response = client.post("/api/v1/tickets/", json=payload)

        assert response.status_code in [401, 403]


class TestTicketRouterRead:
    """查詢工單端點測試"""

    def test_get_tickets_success(self, client, auth_headers):
        """測試成功查詢工單列表"""
        with patch("app.services.ticket_service.TicketService.get_tickets") as mock_get:
            ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Test Ticket",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
            )

            mock_get.return_value = PaginationResponse(
                items=[ticket],
                total=1,
                page=1,
                page_size=10,
                total_pages=1,
                has_next=False,
                has_prev=False,
            )

            response = client.get("/api/v1/tickets/", headers=auth_headers())

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert len(data["items"]) == 1

    def test_get_ticket_by_id_success(self, client, auth_headers):
        """測試成功查詢單一工單（by ID）"""
        with patch("app.services.ticket_service.TicketService.get_ticket_by_id") as mock_get:
            ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Test Ticket",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
            )

            mock_get.return_value = ticket

            response = client.get("/api/v1/tickets/1", headers=auth_headers())

            assert response.status_code == 200
            assert response.json()["ticket_no"] == "TIC-20250101-001"

    def test_get_ticket_by_id_not_found(self, client, auth_headers):
        """測試查詢不存在的工單"""
        with patch("app.services.ticket_service.TicketService.get_ticket_by_id") as mock_get:
            mock_get.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

            response = client.get("/api/v1/tickets/999", headers=auth_headers())

            assert response.status_code == 404

    def test_get_ticket_by_ticket_no_success(self, client, auth_headers):
        """測試成功查詢工單（by ticket_no）"""
        with patch("app.services.ticket_service.TicketService.get_ticket_by_ticket_no") as mock_get:
            ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Test Ticket",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
            )

            mock_get.return_value = ticket

            response = client.get(
                "/api/v1/tickets/by-ticket-no/TIC-20250101-001",
                headers=auth_headers(),
            )

            assert response.status_code == 200
            assert response.json()["ticket_no"] == "TIC-20250101-001"


class TestTicketRouterUpdate:
    """更新工單端點測試"""

    def test_update_ticket_title_success(self, client, auth_headers):
        """測試成功更新工單標題"""
        with patch("app.services.ticket_service.TicketService.update_ticket_title") as mock_update:
            updated_ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Updated Title",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
            )

            mock_update.return_value = updated_ticket

            payload = {"title": "Updated Title"}

            response = client.patch(
                "/api/v1/tickets/1/title",
                json=payload,
                headers=auth_headers(user_id=1),
            )

            assert response.status_code == 200
            assert response.json()["title"] == "Updated Title"

    def test_update_ticket_title_forbidden(self, client, auth_headers):
        """測試非建立者無法更新工單標題"""
        with patch("app.services.ticket_service.TicketService.update_ticket_title") as mock_update:
            mock_update.side_effect = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this ticket",
            )

            payload = {"title": "Updated Title"}

            response = client.patch(
                "/api/v1/tickets/1/title",
                json=payload,
                headers=auth_headers(user_id=2),
            )

            assert response.status_code == 403

    def test_update_ticket_description_success(self, client, auth_headers):
        """測試成功更新工單描述"""
        with patch("app.services.ticket_service.TicketService.update_ticket_description") as mock_update:
            updated_ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Test Ticket",
                description="Updated Description",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
            )

            mock_update.return_value = updated_ticket

            payload = {"description": "Updated Description"}

            response = client.patch(
                "/api/v1/tickets/1/description",
                json=payload,
                headers=auth_headers(user_id=1),
            )

            assert response.status_code == 200
            assert response.json()["description"] == "Updated Description"

    def test_update_ticket_assignee_success(self, client, auth_headers):
        """測試成功更新工單指派對象"""
        with patch("app.services.ticket_service.TicketService.update_ticket_assignee") as mock_update:
            updated_ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Test Ticket",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                assigned_to=2,
                created_by=1,
                created_at=datetime.now(),
            )

            mock_update.return_value = updated_ticket

            payload = {"assigned_to": 2}

            response = client.patch(
                "/api/v1/tickets/1/assignee",
                json=payload,
                headers=auth_headers(user_id=1),
            )

            assert response.status_code == 200
            assert response.json()["assigned_to"] == 2

    def test_update_ticket_labels_success(self, client, auth_headers):
        """測試成功更新工單標籤"""
        with patch("app.services.ticket_service.TicketService.update_ticket_labels") as mock_update:
            updated_ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Test Ticket",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.MEDIUM,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
                labels=[],
            )

            mock_update.return_value = updated_ticket

            payload = {"label_ids": [1, 2]}

            response = client.patch(
                "/api/v1/tickets/1/labels",
                json=payload,
                headers=auth_headers(user_id=1),
            )

            assert response.status_code == 200

    def test_update_full_ticket_success(self, client, auth_headers):
        """測試成功全量更新工單"""
        with patch("app.services.ticket_service.TicketService.update_ticket") as mock_update:
            updated_ticket = TicketRead(
                id=1,
                ticket_no="TIC-20250101-001",
                title="Updated Title",
                description="Updated Description",
                status=TicketStatus.DRAFT,
                priority=TicketPriority.HIGH,
                visibility=TicketVisibility.INTERNAL,
                created_by=1,
                created_at=datetime.now(),
            )

            mock_update.return_value = updated_ticket

            payload = {
                "title": "Updated Title",
                "description": "Updated Description",
                "priority": "high",
            }

            response = client.patch(
                "/api/v1/tickets/1",
                json=payload,
                headers=auth_headers(user_id=1),
            )

            assert response.status_code == 200
            assert response.json()["title"] == "Updated Title"


class TestTicketRouterPermissions:
    """權限相關的測試"""

    def test_unauthorized_without_token(self, client):
        """測試未提供 token 無法訪問"""
        response = client.get("/api/v1/tickets/")
        assert response.status_code in [401, 403]

    def test_non_creator_cannot_update(self, client, auth_headers):
        """測試非建立者無法更新工單"""
        with patch("app.services.ticket_service.TicketService.update_ticket_title") as mock_update:
            mock_update.side_effect = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this ticket",
            )

            payload = {"title": "New Title"}

            response = client.patch(
                "/api/v1/tickets/1/title",
                json=payload,
                headers=auth_headers(user_id=999),  # 非建立者
            )

            assert response.status_code == 403


class TestTicketRouterValidation:
    """驗證相關的測試"""

    def test_invalid_priority(self, client, auth_headers):
        """測試無效的優先級"""
        payload = {
            "title": "Test Ticket",
            "priority": "INVALID_PRIORITY",
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(),
        )

        assert response.status_code == 422

    def test_empty_title(self, client, auth_headers):
        """測試空標題"""
        payload = {
            "title": "",
            "description": "Test",
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(),
        )

        assert response.status_code == 422

    def test_title_too_long(self, client, auth_headers):
        """測試過長的標題"""
        payload = {
            "title": "x" * 201,  # 超過 max_length=200
            "description": "Test",
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(),
        )

        assert response.status_code == 422
