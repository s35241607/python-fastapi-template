#!/usr/bin/env python3
"""
Ticket System 使用範例
展示複雜的 CRUD 操作
"""

import asyncio
import json

from fastapi.testclient import TestClient

from app.main import app


async def example_usage():
    client = TestClient(app)

    print("=== FastAPI Ticket System 範例 ===\n")

    # 注意：實際使用需要先設定資料庫並運行 init_db.py
    # 這裡只是展示 API 結構

    print("1. 建立 Ticket 與初始 Comment:")
    ticket_data = {
        "ticket": {"title": "系統錯誤修復", "description": "應用程式在特定情況下崩潰", "user_id": 1},
        "initial_comment": {"content": "發現錯誤，需要緊急修復", "user_id": 1},
    }
    print(json.dumps(ticket_data, indent=2, ensure_ascii=False))

    print("\n2. 更新 Ticket 狀態:")
    print("PUT /api/v1/tickets/1/status?user_id=1")
    print('Body: "in_progress"')

    print("\n3. 為 Ticket 添加 Comment:")
    comment_data = {"content": "已經開始調查問題", "user_id": 2}
    print(json.dumps(comment_data, indent=2, ensure_ascii=False))

    print("\n4. 獲取 Ticket 詳細資訊 (包含所有關聯):")
    print("GET /api/v1/tickets/1")

    print("\n5. 刪除 Ticket (級聯刪除所有 Comments):")
    print("DELETE /api/v1/tickets/1?user_id=1")

    print("\n=== 架構特點 ===")
    print("- Router > Service > Repository 三層架構")
    print("- Async PostgreSQL 資料庫操作")
    print("- 複雜 CRUD: 多表關聯操作")
    print("- 自動級聯刪除")
    print("- 狀態追蹤與系統 Comments")


if __name__ == "__main__":
    asyncio.run(example_usage())
