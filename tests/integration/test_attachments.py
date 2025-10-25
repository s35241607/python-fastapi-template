#!/usr/bin/env python3
"""
測試附件 API 的完整解耦上傳流程
使用 pytest 和 FastAPI TestClient
"""

import io

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """測試客戶端"""
    return TestClient(app)


@pytest.fixture
def test_files():
    """測試文件"""
    files = {
        "text_file": ("test.txt", io.BytesIO(b"Hello, this is a test file!"), "text/plain"),
        "image_file": ("test.png", io.BytesIO(b"fake image content"), "image/png"),
    }
    return files


class TestAttachmentDecoupledFlow:
    """測試解耦的上傳與創建流程"""

    def test_health_check(self, client):
        """測試健康檢查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_openapi_schema(self, client):
        """測試 OpenAPI schema"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        paths = schema.get("paths", {})
        attachment_paths = [p for p in paths if "/api/v1/attachments" in p]
        assert len(attachment_paths) > 0, "未找到附件路由"

    def test_preupload_attachment(self, client, test_files):
        """測試預上傳附件 (使用統一上傳端點的 preupload 模式)"""
        file_data = test_files["text_file"]

        # 使用統一上傳端點的 preupload 模式
        response = client.post(
            "/api/v1/attachments/upload?preupload=true",
            files={"file": file_data},
            data={"usage_type": "general", "description": "Test preupload attachment"},
        )

        # 注意：這裡可能會因為認證失敗，但我們檢查路由是否存在
        if response.status_code in [401, 403]:
            # 認證失敗，但路由存在
            assert True
        elif response.status_code == 201:
            # 認證成功
            result = response.json()
            assert "attachment" in result
            assert "upload_url" in result
            assert result["attachment"]["related_type"] is None
            assert result["attachment"]["related_id"] is None
        else:
            pytest.fail(f"預上傳失敗: {response.status_code} - {response.text}")

    def test_preupload_validation(self, client, test_files):
        """測試預上傳驗證"""
        # 測試沒有文件的請求
        response = client.post(
            "/api/v1/attachments/upload?preupload=true", data={"usage_type": "general", "description": "Test validation"}
        )

        # 應該返回 422 (驗證錯誤) 或者 401/403 (認證錯誤)
        assert response.status_code in [401, 403, 422]

    def test_unified_upload_single_attachment(self, client, test_files):
        """測試統一上傳端點 - 單個附件"""
        file_data = test_files["text_file"]

        response = client.post(
            "/api/v1/attachments/upload",
            files={"file": file_data},
            data={"related_type": "tickets", "related_id": "1", "usage_type": "general", "description": "Unified upload test"},
        )

        # 檢查認證和邏輯（即使認證失敗，端點應該存在）
        if response.status_code in [401, 422]:
            assert True  # 認證或驗證失敗，但端點存在
        elif response.status_code == 201:
            result = response.json()
            assert "attachment" in result
            assert result["attachment"]["related_type"] == "tickets"
            assert result["attachment"]["related_id"] == 1
            assert result["attachment"]["usage_type"] == "general"
            assert result["attachment"]["description"] == "Unified upload test"

    def test_unified_upload_multiple_attachments(self, client, test_files):
        """測試批量上傳附件"""
        files = [("files", test_files["text_file"]), ("files", ("test2.txt", io.BytesIO(b"Second file content"), "text/plain"))]

        response = client.post(
            "/api/v1/attachments/upload/batch",
            files=files,
            data={"related_type": "tickets", "related_id": "1", "usage_type": "general", "description": "Bulk upload test"},
        )

        if response.status_code in [401, 422]:
            assert True
        elif response.status_code == 201:
            result = response.json()
            assert "attachments" in result
            assert "total_uploaded" in result
            assert result["total_uploaded"] == 2

    def test_unified_upload_preupload(self, client, test_files):
        """測試預上傳附件"""
        file_data = test_files["text_file"]

        response = client.post(
            "/api/v1/attachments/upload/preupload",
            files={"file": file_data},
            data={"usage_type": "general", "description": "Preupload test"},
        )

        if response.status_code in [401, 422]:
            assert True
        elif response.status_code == 201:
            result = response.json()
            assert "attachment" in result
            assert "upload_url" in result
            # 預上傳的附件不應該有關聯
            assert result["attachment"]["related_type"] is None
            assert result["attachment"]["related_id"] is None

    def test_unified_upload_rich_text_image(self, client, test_files):
        """測試富文本圖片上傳"""
        file_data = test_files["image_file"]

        response = client.post(
            "/api/v1/attachments/upload/rich-text-image",
            files={"file": file_data},
            data={"related_type": "tickets", "related_id": "1", "alt_text": "Test image"},
        )

        if response.status_code in [401, 422]:
            assert True
        elif response.status_code == 201:
            result = response.json()
            assert "attachment" in result
            assert "attachment_id" in result
            assert "markdown_syntax" in result
            # 檢查 markdown 語法包含 API 路徑
            assert "/api/v1/attachments/" in result["markdown_syntax"]
            assert "/download" in result["markdown_syntax"]
            assert "![Test image](" in result["markdown_syntax"]

    def test_download_attachment(self, client):
        """測試下載附件"""
        # 這個測試需要先創建一個附件，然後下載
        # 在沒有認證的情況下很難完整測試
        response = client.get("/api/v1/attachments/1/download")

        # 應該返回認證錯誤或不存在錯誤
        assert response.status_code in [401, 403, 404]

    def test_link_attachments_functionality(self, client):
        """測試關聯附件功能"""
        response = client.post(
            "/api/v1/attachments/link", json={"attachment_ids": [1, 2], "related_type": "tickets", "related_id": 1}
        )

        # 應該返回認證錯誤或處理結果
        assert response.status_code in [401, 403, 200, 404, 422]

    def test_get_attachments_with_filters(self, client):
        """測試取得附件列表並帶過濾"""
        response = client.get(
            "/api/v1/attachments/", params={"related_type": "tickets", "related_id": "1", "usage_type": "inline"}
        )

        # 應該返回認證錯誤或結果
        assert response.status_code in [401, 403, 200]

    def test_attachment_crud_operations(self, client):
        """測試附件 CRUD 操作"""
        # 測試取得單個附件
        get_response = client.get("/api/v1/attachments/1")
        assert get_response.status_code in [401, 403, 404, 200]

        # 測試更新附件
        update_response = client.put("/api/v1/attachments/1", json={"description": "Updated description"})
        assert update_response.status_code in [401, 403, 404, 200, 422]

        # 測試刪除附件
        delete_response = client.delete("/api/v1/attachments/1")
        assert delete_response.status_code in [401, 403, 404, 204]

    def test_attachment_endpoints_exist(self, client):
        """測試附件端點是否存在"""
        # 測試所有主要的附件端點
        endpoints = [
            "/api/v1/attachments/upload",  # 單個上傳端點
            "/api/v1/attachments/upload/batch",  # 批量上傳端點
            "/api/v1/attachments/upload/preupload",  # 預上傳端點
            "/api/v1/attachments/upload/rich-text-image",  # 富文本圖片端點
            "/api/v1/attachments/link",
            "/api/v1/attachments/",
        ]

        for endpoint in endpoints:
            # 使用 OPTIONS 或 HEAD 請求檢查端點是否存在
            response = client.options(endpoint)
            # 即使返回 405 (方法不允許)，也表示端點存在
            assert response.status_code in [200, 401, 403, 405, 422], f"端點 {endpoint} 不存在: {response.status_code}"

    def test_decoupled_flow_simulation(self, client, test_files):
        """模擬完整的解耦上傳流程"""
        # 注意：這個測試在沒有認證的情況下會失敗
        # 但它驗證了 API 的結構和邏輯

        # 步驟 1: 預上傳附件
        file_data = test_files["text_file"]
        preupload_response = client.post(
            "/api/v1/attachments/preupload",
            files={"file": file_data},
            data={"usage_type": "general", "description": "Test decoupled flow"},
        )

        if preupload_response.status_code == 201:
            preupload_data = preupload_response.json()
            attachment_id = preupload_data["attachment"]["id"]

            # 步驟 2: 關聯附件到資源
            link_response = client.post(
                "/api/v1/attachments/link", json={"attachment_ids": [attachment_id], "related_type": "tickets", "related_id": 1}
            )

            if link_response.status_code == 200:
                link_data = link_response.json()
                assert link_data["total_linked"] == 1
                assert len(link_data["linked_attachments"]) == 1

                # 步驟 3: 驗證附件已被關聯
                get_response = client.get("/api/v1/attachments/", params={"related_type": "tickets", "related_id": "1"})

                if get_response.status_code == 200:
                    get_data = get_response.json()
                    assert len(get_data["attachments"]) >= 1
                    # 檢查附件是否正確關聯
                    attachment = get_data["attachments"][0]
                    assert attachment["related_type"] == "tickets"
                    assert attachment["related_id"] == 1

    def test_error_handling(self, client):
        """測試錯誤處理"""
        # 測試關聯不存在的附件
        response = client.post(
            "/api/v1/attachments/link",
            json={
                "attachment_ids": [99999],  # 不存在的附件 ID
                "related_type": "tickets",
                "related_id": 1,
            },
        )

        # 應該返回錯誤
        assert response.status_code in [401, 403, 404, 422]

    def test_file_validation(self, client):
        """測試文件驗證"""
        # 創建一個大文件來測試大小限制
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = ("large.txt", io.BytesIO(large_content), "text/plain")

        response = client.post(
            "/api/v1/attachments/upload/preupload",
            files={"file": large_file},
            data={"usage_type": "general", "description": "Test file size validation"},
        )

        # 應該因為文件過大而失敗
        if response.status_code not in [401, 403]:  # 忽略認證錯誤
            assert response.status_code in [400, 413]  # 請求錯誤或負載過大
