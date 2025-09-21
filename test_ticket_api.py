"""
測試 Ticket API 功能
"""

import asyncio
import json
from datetime import datetime

import aiohttp


BASE_URL = "http://localhost:8000/api/v1"
TEST_TOKEN = "test-token"  # 假設的測試 token


async def test_ticket_api():
    """測試工單 API"""
    print("🧪 開始測試 Ticket API...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 測試創建工單
        print("\n1. 測試創建工單...")
        ticket_data = {
            "title": "測試工單",
            "description": "這是一個測試工單",
            "priority": "medium",
            "visibility": "internal",
            "custom_fields_data": {"test_field": "test_value"}
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/tickets/",
                json=ticket_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    ticket_id = result["id"]
                    ticket_no = result["ticket_no"]
                    print(f"✅ 工單創建成功: ID={ticket_id}, NO={ticket_no}")
                    
                    # 2. 測試獲取工單詳情
                    print(f"\n2. 測試獲取工單詳情 (ID: {ticket_id})...")
                    async with session.get(
                        f"{BASE_URL}/tickets/{ticket_id}",
                        headers=headers
                    ) as get_response:
                        if get_response.status == 200:
                            ticket_detail = await get_response.json()
                            print(f"✅ 工單詳情獲取成功: {ticket_detail['title']}")
                        else:
                            error = await get_response.text()
                            print(f"❌ 工單詳情獲取失敗: {error}")
                    
                    # 3. 測試根據工單號碼查詢
                    print(f"\n3. 測試根據工單號碼查詢 (NO: {ticket_no})...")
                    async with session.get(
                        f"{BASE_URL}/tickets/by-ticket-no/{ticket_no}",
                        headers=headers
                    ) as no_response:
                        if no_response.status == 200:
                            ticket_by_no = await no_response.json()
                            print(f"✅ 工單號碼查詢成功: {ticket_by_no['title']}")
                        else:
                            error = await no_response.text()
                            print(f"❌ 工單號碼查詢失敗: {error}")
                    
                    # 4. 測試更新工單
                    print(f"\n4. 測試更新工單 (ID: {ticket_id})...")
                    update_data = {
                        "title": "更新後的測試工單",
                        "priority": "high"
                    }
                    async with session.put(
                        f"{BASE_URL}/tickets/{ticket_id}",
                        json=update_data,
                        headers=headers
                    ) as update_response:
                        if update_response.status == 200:
                            updated_ticket = await update_response.json()
                            print(f"✅ 工單更新成功: {updated_ticket['title']}")
                        else:
                            error = await update_response.text()
                            print(f"❌ 工單更新失敗: {error}")
                    
                    # 5. 測試狀態轉換
                    print(f"\n5. 測試狀態轉換 (ID: {ticket_id})...")
                    status_data = {
                        "status": "open",
                        "comment": "直接開啟工單"
                    }
                    async with session.patch(
                        f"{BASE_URL}/tickets/{ticket_id}/status",
                        json=status_data,
                        headers=headers
                    ) as status_response:
                        if status_response.status == 200:
                            status_result = await status_response.json()
                            print(f"✅ 狀態轉換成功: {status_result['status']}")
                        else:
                            error = await status_response.text()
                            print(f"❌ 狀態轉換失敗: {error}")
                    
                else:
                    error = await response.text()
                    print(f"❌ 工單創建失敗: {error}")
                    return
                    
        except Exception as e:
            print(f"❌ 創建工單時發生錯誤: {e}")
            return
        
        # 6. 測試工單搜尋
        print("\n6. 測試工單搜尋...")
        try:
            async with session.get(
                f"{BASE_URL}/tickets/?page=1&size=10",
                headers=headers
            ) as search_response:
                if search_response.status == 200:
                    search_result = await search_response.json()
                    print(f"✅ 工單搜尋成功: 找到 {search_result['total']} 個工單")
                else:
                    error = await search_response.text()
                    print(f"❌ 工單搜尋失敗: {error}")
        except Exception as e:
            print(f"❌ 搜尋工單時發生錯誤: {e}")
        
        # 7. 測試工單統計
        print("\n7. 測試工單統計...")
        try:
            async with session.get(
                f"{BASE_URL}/tickets/stats/summary",
                headers=headers
            ) as stats_response:
                if stats_response.status == 200:
                    stats_result = await stats_response.json()
                    print(f"✅ 工單統計成功: 總數 {stats_result['total']}")
                    print(f"   按狀態統計: {stats_result['by_status']}")
                else:
                    error = await stats_response.text()
                    print(f"❌ 工單統計失敗: {error}")
        except Exception as e:
            print(f"❌ 獲取統計時發生錯誤: {e}")


if __name__ == "__main__":
    print("請確保 FastAPI 伺服器正在運行於 http://localhost:8000")
    asyncio.run(test_ticket_api())