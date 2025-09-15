#!/usr/bin/env python3
"""
重構後的 Schemas 使用範例
展示新的模組化結構
"""

from app.schemas.user import User, UserCreate, UserBase
from app.schemas.ticket import Ticket, TicketCreate, TicketUpdate, TicketWithInitialComment
from app.schemas.comment import Comment, CommentCreate, CommentBase
from app.models.ticket import TicketStatus

def demonstrate_schemas():
    print("🎯 重構後的 Schemas 結構展示\n")

    # User schemas
    print("👤 User Schemas:")
    user_create = UserCreate(name="張三", email="zhangsan@example.com")
    print(f"  UserCreate: {user_create}")

    # Ticket schemas
    print("\n🎫 Ticket Schemas:")
    ticket_create = TicketCreate(
        title="系統錯誤修復",
        description="應用程式崩潰問題",
        user_id=1
    )
    print(f"  TicketCreate: {ticket_create}")

    ticket_update = TicketUpdate(
        status=TicketStatus.IN_PROGRESS,
        description="正在調查中..."
    )
    print(f"  TicketUpdate: {ticket_update}")

    # Comment schemas
    print("\n💬 Comment Schemas:")
    comment_create = CommentCreate(
        content="已開始處理這個問題",
        user_id=1
    )
    print(f"  CommentCreate: {comment_create}")

    # Complex schema
    print("\n🔗 Complex Schema (Ticket with Initial Comment):")
    try:
        # 手動建立資料結構來展示
        complex_data = {
            "ticket": ticket_create.model_dump(),
            "initial_comment": comment_create.model_dump()
        }
        print(f"  Complex data: {complex_data}")
    except Exception as e:
        print(f"  Complex schema demo: {str(e)}")

    print("\n📁 檔案結構:")
    print("  app/schemas/")
    print("  ├── __init__.py      # 統一匯入")
    print("  ├── user.py          # User 相關 schemas")
    print("  ├── ticket.py        # Ticket 相關 schemas")
    print("  └── comment.py       # Comment 相關 schemas")

    print("\n✅ 所有 schemas 都支援 Pydantic 驗證和序列化")

if __name__ == "__main__":
    demonstrate_schemas()
