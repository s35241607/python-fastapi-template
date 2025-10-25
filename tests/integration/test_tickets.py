"""
Ticket API 集成測試

使用真實資料庫（PostgreSQL）進行端到端測試。
"""

import pytest


@pytest.mark.integration
class TestTicketIntegration:
    """Ticket API 集成測試"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """在每個測試方法之前清理數據庫"""
        from sqlalchemy import create_engine, text

        # 使用同步引擎進行清理以避免事件循環問題
        test_db_url = "postgresql://postgres:password@localhost:5433/test_fastapi"
        engine = create_engine(test_db_url)

        # 只清理數據，不重新創建 schema（schema 由 conftest.py 中的 test_engine fixture 創建）
        with engine.begin() as conn:
            # 刪除所有數據但保留 schema
            conn.execute(text("TRUNCATE TABLE ticket.tickets CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.categories CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.labels CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.ticket_categories CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.ticket_labels CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.ticket_notes CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.attachments CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.ticket_view_permissions CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.approval_processes CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.approval_process_steps CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.approval_process_step_approvers CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.notification_rules CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.notification_rule_users CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.notification_rule_roles CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.ticket_templates CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.ticket_template_categories CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.ticket_template_labels CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.approval_templates CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.approval_template_steps CASCADE"))
            conn.execute(text("TRUNCATE TABLE ticket.approval_template_step_approvers CASCADE"))

        engine.dispose()

    @pytest.mark.asyncio
    async def test_create_and_retrieve_ticket(self, client, auth_headers):
        """測試建立並查詢工單"""
        # 建立工單
        payload = {
            "title": "Integration Test Ticket",
            "description": "Test Description",
            "priority": "high",
            "visibility": "internal",
            "category_ids": [],
            "label_ids": [],
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(user_id=1),
        )

        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        assert response.status_code == 201
        created_ticket = response.json()
        ticket_id = created_ticket["id"]
        ticket_no = created_ticket["ticket_no"]

        # 查詢工單
        response = client.get(
            f"/api/v1/tickets/{ticket_id}",
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 200
        retrieved_ticket = response.json()
        assert retrieved_ticket["title"] == "Integration Test Ticket"
        assert retrieved_ticket["ticket_no"] == ticket_no

    @pytest.mark.asyncio
    async def test_create_ticket_with_categories_and_labels(
        self, client, auth_headers, async_db_session, sample_categories, sample_labels
    ):
        """測試建立含有分類和標籤的工單"""
        # 準備數據
        category_ids = [sample_categories[0].id, sample_categories[1].id]
        label_ids = [sample_labels[0].id]

        payload = {
            "title": "Ticket with Categories and Labels",
            "description": "Test",
            "priority": "medium",
            "category_ids": category_ids,
            "label_ids": label_ids,
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 201
        ticket = response.json()

        # 驗證關聯資料
        assert len(ticket["categories"]) == 2
        assert len(ticket["labels"]) == 1

    @pytest.mark.asyncio
    async def test_list_tickets_pagination(self, client, auth_headers, sample_tickets):
        """測試工單列表分頁"""
        # 查詢第一頁
        response = client.get(
            "/api/v1/tickets/?page=1&page_size=2",
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["page_size"] == 2

    @pytest.mark.asyncio
    async def test_list_tickets_filtering(self, client, auth_headers, sample_tickets):
        """測試工單列表篩選"""
        # 篩選狀態為 DRAFT 的工單
        response = client.get(
            "/api/v1/tickets/?status=draft",
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 200
        data = response.json()
        # 假設只有第一個工單是 DRAFT
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_tickets_sorting(self, client, auth_headers, sample_tickets):
        """測試工單列表排序"""
        response = client.get(
            "/api/v1/tickets/?sort_by=created_at&sort_order=asc",
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0

    @pytest.mark.asyncio
    async def test_update_ticket_title(self, client, auth_headers, sample_ticket):
        """測試更新工單標題"""
        new_title = "Updated Ticket Title"

        payload = {"title": new_title}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}/title",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert updated_ticket["title"] == new_title

    @pytest.mark.asyncio
    async def test_update_ticket_description(self, client, auth_headers, sample_ticket):
        """測試更新工單描述"""
        new_description = "Updated Description"

        payload = {"description": new_description}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}/description",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert updated_ticket["description"] == new_description

    @pytest.mark.asyncio
    async def test_update_ticket_assignee(self, client, auth_headers, sample_ticket):
        """測試更新工單指派對象"""
        new_assignee = 2

        payload = {"assigned_to": new_assignee}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}/assignee",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert updated_ticket["assigned_to"] == new_assignee

    def test_update_ticket_labels(self, client, auth_headers, sample_ticket):
        """測試更新工單標籤"""
        # 創建測試標籤
        label_payload_1 = {"name": "Test Label 1", "color": "#FF0000", "description": "Test label 1"}
        label_response_1 = client.post(
            "/api/v1/labels/",
            json=label_payload_1,
            headers=auth_headers(user_id=1),
        )
        assert label_response_1.status_code == 201
        label_data_1 = label_response_1.json()

        label_payload_2 = {"name": "Test Label 2", "color": "#00FF00", "description": "Test label 2"}
        label_response_2 = client.post(
            "/api/v1/labels/",
            json=label_payload_2,
            headers=auth_headers(user_id=1),
        )
        assert label_response_2.status_code == 201
        label_data_2 = label_response_2.json()

        new_label_ids = [label_data_1["id"], label_data_2["id"]]

        payload = {"label_ids": new_label_ids}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}/labels",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert len(updated_ticket["labels"]) == 2

    def test_full_ticket_update(self, client, auth_headers, sample_ticket):
        """測試全量更新工單"""
        payload = {
            "title": "Fully Updated Title",
            "description": "Fully Updated Description",
            "priority": "low",
        }

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert updated_ticket["title"] == "Fully Updated Title"
        assert updated_ticket["description"] == "Fully Updated Description"
        assert updated_ticket["priority"] == "low"

    @pytest.mark.asyncio
    async def test_get_ticket_by_ticket_no(self, client, auth_headers, sample_ticket):
        """測試按 ticket_no 查詢工單"""
        response = client.get(
            f"/api/v1/tickets/by-ticket-no/{sample_ticket.ticket_no}",
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 200
        ticket = response.json()
        assert ticket["ticket_no"] == sample_ticket.ticket_no


@pytest.mark.integration
class TestTicketPermissions:
    """工單權限相關的集成測試"""

    @pytest.mark.asyncio
    async def test_non_creator_cannot_update(self, client, auth_headers, sample_ticket):
        """測試非建立者無法更新工單"""
        payload = {"title": "Unauthorized Update"}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}/title",
            json=payload,
            headers=auth_headers(user_id=999),  # 非建立者
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_creator_can_update(self, client, auth_headers, sample_ticket):
        """測試建立者可以更新工單"""
        payload = {"title": "Creator Update"}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}/title",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert updated_ticket["title"] == "Creator Update"


@pytest.mark.integration
class TestTicketErrorHandling:
    """錯誤處理的集成測試"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_ticket(self, client, auth_headers):
        """測試查詢不存在的工單"""
        response = client.get(
            "/api/v1/tickets/99999",
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_nonexistent_ticket_by_no(self, client, auth_headers):
        """測試按不存在的 ticket_no 查詢"""
        response = client.get(
            "/api/v1/tickets/by-ticket-no/TIC-99999999-999",
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_nonexistent_ticket(self, client, auth_headers):
        """測試更新不存在的工單"""
        payload = {"title": "Updated"}

        response = client.patch(
            "/api/v1/tickets/99999/title",
            json=payload,
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_priority_enum(self, client, auth_headers):
        """測試無效的優先級列舉值"""
        payload = {
            "title": "Test",
            "priority": "INVALID_PRIORITY",
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_title(self, client, auth_headers):
        """測試空標題"""
        payload = {
            "title": "",
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_title_exceeds_max_length(self, client, auth_headers):
        """測試標題超過最大長度"""
        payload = {
            "title": "x" * 201,  # max_length=200
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestTicketRelationships:
    """工單關聯資料的集成測試"""

    @pytest.mark.asyncio
    async def test_ticket_with_multiple_categories(self, client, auth_headers, async_db_session, sample_categories):
        """測試工單含有多個分類"""
        category_ids = [c.id for c in sample_categories]

        payload = {
            "title": "Multi-Category Ticket",
            "category_ids": category_ids,
            "label_ids": [],
        }

        response = client.post(
            "/api/v1/tickets/",
            json=payload,
            headers=auth_headers(user_id=1),
        )

        assert response.status_code == 201
        ticket = response.json()
        assert len(ticket["categories"]) == len(sample_categories)

    def test_update_ticket_categories(self, client, auth_headers, sample_ticket):
        """測試更新工單分類"""
        # 創建一個測試分類
        category_payload = {"name": "Test Category for Update", "description": "Test category"}
        category_response = client.post(
            "/api/v1/categories/",
            json=category_payload,
            headers=auth_headers(user_id=1),
        )
        assert category_response.status_code == 201
        category_data = category_response.json()
        category_id = category_data["id"]

        payload = {
            "category_ids": [category_id],
        }

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert len(updated_ticket["categories"]) == 1

    def test_remove_all_labels(self, client, auth_headers, sample_ticket):
        """測試移除工單所有標籤"""
        payload = {"label_ids": []}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}/labels",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert len(updated_ticket["labels"]) == 0


@pytest.mark.integration
class TestTicketPartialUpdates:
    """部分更新相關的集成測試"""

    def test_partial_update_only_title(self, client, auth_headers, sample_ticket):
        """測試只更新標題（其他欄位保持不變）"""
        original_description = sample_ticket.description
        new_title = "Only Title Changed"

        payload = {"title": new_title}

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert updated_ticket["title"] == new_title
        assert updated_ticket["description"] == original_description

    def test_partial_update_priority_and_description(self, client, auth_headers, sample_ticket):
        """測試只更新優先級和描述"""
        new_priority = "low"
        new_description = "Only These Fields Changed"

        payload = {
            "priority": new_priority,
            "description": new_description,
        }

        response = client.patch(
            f"/api/v1/tickets/{sample_ticket.id}",
            json=payload,
            headers=auth_headers(user_id=sample_ticket.created_by),
        )

        assert response.status_code == 200
        updated_ticket = response.json()
        assert updated_ticket["priority"] == new_priority
        assert updated_ticket["description"] == new_description
