# Ticket 系統開發計劃 (修訂版)

**版本**: v2.0
**建立日期**: 2025-09-28
**修訂日期**: 2025-09-28
**基於規格**: SPEC.md v1.0
**基於現有專案**: python-fastapi-template
**開發策略**: 增量式開發，從簡單功能開始

## 📊 現有專案進度分析

### ✅ **已完成的基礎設施**
- **資料庫 Schema** - 完整的 ticket 系統表結構 (68d74054af42_001_init.py)
- **模型定義** - Ticket, Category, Label 等完整 SQLAlchemy 模型
- **枚舉定義** - 所有狀態、優先級、事件類型枚舉
- **MVC 範例** - Category/Label 的完整 Repository→Service→Router→Schema 架構
- **基礎設施** - Database, Config, Dependencies 完整設定

### ❌ **待實作功能**
- **Ticket CRUD** - Repository, Service, Router, Schema
- **基本 API 端點** - 建立、查詢、更新 Ticket
- **簡單權限控制** - 基礎的可見性檢查

## 🎯 簡化開發策略

採用 **增量式開發**，基於現有架構模式快速實作核心功能：
1. **照抄現有模式** - 參考 Category/Label 的實作模式
2. **先簡後繁** - 先實作基本 CRUD，後續再加簽核和進階權限
3. **一步一步來** - 每次只實作一個小功能，立即測試

## 階段一：基礎 Ticket CRUD (第一天)

### 1.1 建立 Ticket Schema 📋
- **預估時間**: 30 分鐘
- **參考範例**: `app/schemas/category.py`

#### 具體任務：
- [ ] 建立 `app/schemas/ticket.py`
- [ ] 定義 `TicketBase`, `TicketCreate`, `TicketUpdate`, `TicketResponse`
- [ ] 基礎欄位驗證 (title 必填、description 可選等)

```python
# app/schemas/ticket.py 預覽
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.models.enums import TicketStatus, TicketPriority, TicketVisibility

class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    visibility: TicketVisibility = TicketVisibility.INTERNAL
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None

class TicketCreate(TicketBase):
    # Template 相關
    ticket_template_id: Optional[int] = None
    approval_template_id: Optional[int] = None
    custom_fields_data: Optional[Dict[str, Any]] = None

    # Category 和 Label 關聯 (使用 ID 列表)
    category_ids: List[int] = Field(default_factory=list)
    label_ids: List[int] = Field(default_factory=list)

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TicketPriority] = None
    visibility: Optional[TicketVisibility] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    custom_fields_data: Optional[Dict[str, Any]] = None

    # Category 和 Label 更新 (可選)
    category_ids: Optional[List[int]] = None
    label_ids: Optional[List[int]] = None

class TicketResponse(TicketBase):
    id: int
    ticket_no: str
    status: TicketStatus
    ticket_template_id: Optional[int] = None
    approval_template_id: Optional[int] = None
    custom_fields_data: Optional[Dict[str, Any]] = None

    # 建立/更新資訊
    created_by: int
    created_at: datetime
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    # 關聯資料 (如果需要，可以包含完整的 category 和 label 物件)
    categories: Optional[List[Dict[str, Any]]] = None  # CategoryRead 的資料
    labels: Optional[List[Dict[str, Any]]] = None      # LabelRead 的資料

    class Config:
        from_attributes = True

# 狀態變更專用的 Schema
class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    reason: Optional[str] = Field(None, max_length=500, description="狀態變更原因")
```### 1.2 建立 Ticket Repository 💾
- **預估時間**: 45 分鐘
- **參考範例**: `app/repositories/category_repository.py`

#### 具體任務：
- [ ] 建立 `app/repositories/ticket_repository.py`
- [ ] 繼承 `BaseRepository`
- [ ] 實作基本 CRUD 方法
- [ ] 加入 `ticket_no` 自動生成邏輯

```python
# app/repositories/ticket_repository.py 預覽
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
from app.models.ticket import Ticket
from app.models.category import Category
from app.models.label import Label
from app.repositories.base_repository import BaseRepository

class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: Session):
        super().__init__(db, Ticket)

    def generate_ticket_no(self) -> str:
        """生成唯一的工單號碼: T + YYYYMMDD + 4位序號"""
        today = datetime.now().strftime("%Y%m%d")
        # 查詢今天已有的工單數量
        today_count = self.db.query(Ticket).filter(
            Ticket.ticket_no.like(f"T{today}%")
        ).count()

        sequence = str(today_count + 1).zfill(4)
        return f"T{today}{sequence}"

    def get_by_ticket_no(self, ticket_no: str) -> Optional[Ticket]:
        return self.db.query(Ticket).filter(Ticket.ticket_no == ticket_no).first()

    def get_by_created_by(self, created_by: int) -> List[Ticket]:
        return self.db.query(Ticket).filter(
            and_(Ticket.created_by == created_by, Ticket.deleted_at.is_(None))
        ).all()

    def get_with_relations(self, ticket_id: int) -> Optional[Ticket]:
        """取得包含 categories 和 labels 關聯的工單"""
        return self.db.query(Ticket).options(
            joinedload(Ticket.categories),
            joinedload(Ticket.labels)
        ).filter(Ticket.id == ticket_id).first()

    def add_categories(self, ticket: Ticket, category_ids: List[int]) -> None:
        """為工單新增分類"""
        categories = self.db.query(Category).filter(Category.id.in_(category_ids)).all()
        ticket.categories.extend(categories)
        self.db.commit()

    def add_labels(self, ticket: Ticket, label_ids: List[int]) -> None:
        """為工單新增標籤"""
        labels = self.db.query(Label).filter(Label.id.in_(label_ids)).all()
        ticket.labels.extend(labels)
        self.db.commit()

    def update_categories(self, ticket: Ticket, category_ids: List[int]) -> None:
        """更新工單的分類 (完全替換)"""
        ticket.categories.clear()
        if category_ids:
            categories = self.db.query(Category).filter(Category.id.in_(category_ids)).all()
            ticket.categories.extend(categories)
        self.db.commit()

    def update_labels(self, ticket: Ticket, label_ids: List[int]) -> None:
        """更新工單的標籤 (完全替換)"""
        ticket.labels.clear()
        if label_ids:
            labels = self.db.query(Label).filter(Label.id.in_(label_ids)).all()
            ticket.labels.extend(labels)
        self.db.commit()
```### 1.3 建立 Ticket Service 🔧
- **預估時間**: 45 分鐘
- **參考範例**: `app/services/category_service.py`

#### 具體任務：
- [ ] 建立 `app/services/ticket_service.py`
- [ ] 實作基本業務邏輯
- [ ] 自動生成 `ticket_no`
- [ ] 簡單的權限檢查 (基於 created_by)

```python
# app/services/ticket_service.py 預覽
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketStatusUpdate
from app.repositories.ticket_repository import TicketRepository
from app.models.ticket import Ticket
from app.models.enums import TicketStatus, TicketVisibility

class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketRepository(db)

    async def create_ticket(self, ticket_data: TicketCreate, created_by: int) -> Ticket:
        """建立新工單，包含分類和標籤關聯"""
        try:
            # 1. 生成唯一工單號
            ticket_no = self.repository.generate_ticket_no()

            # 2. 建立工單基本資料 (排除關聯欄位)
            ticket_dict = ticket_data.model_dump(exclude={"category_ids", "label_ids"})
            ticket_dict.update({
                "ticket_no": ticket_no,
                "created_by": created_by,
                "status": TicketStatus.DRAFT
            })

            ticket = Ticket(**ticket_dict)

            # 3. 先儲存工單
            self.db.add(ticket)
            self.db.commit()
            self.db.refresh(ticket)

            # 4. 處理分類和標籤關聯
            if ticket_data.category_ids:
                self.repository.add_categories(ticket, ticket_data.category_ids)

            if ticket_data.label_ids:
                self.repository.add_labels(ticket, ticket_data.label_ids)

            # 5. 回傳包含關聯資料的工單
            return self.repository.get_with_relations(ticket.id)

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"建立工單失敗: {str(e)}"
            )

    async def get_ticket_by_id(self, ticket_id: int, current_user_id: int) -> Optional[Ticket]:
        """取得單一工單 (含權限檢查)"""
        ticket = self.repository.get_with_relations(ticket_id)
        if not ticket:
            return None

        # 基礎權限檢查
        if not self._can_view_ticket(ticket, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="沒有權限查看此工單"
            )

        return ticket

    async def get_user_tickets(self, created_by: int, current_user_id: int) -> List[Ticket]:
        """取得用戶建立的工單列表"""
        # 簡單權限檢查：只能查看自己建立的工單 (後續可擴展)
        if created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能查看自己建立的工單"
            )

        return self.repository.get_by_created_by(created_by)

    async def update_ticket(self, ticket_id: int, ticket_data: TicketUpdate, current_user_id: int) -> Optional[Ticket]:
        """更新工單資料"""
        ticket = self.repository.get_by_id(ticket_id)
        if not ticket:
            return None

        # 權限檢查：只有建立者可以編輯 (後續可擴展)
        if ticket.created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有工單建立者可以編輯"
            )

        try:
            # 更新基本欄位
            update_data = ticket_data.model_dump(exclude_unset=True, exclude={"category_ids", "label_ids"})
            for field, value in update_data.items():
                setattr(ticket, field, value)

            ticket.updated_by = current_user_id

            # 處理分類和標籤關聯更新
            if ticket_data.category_ids is not None:
                self.repository.update_categories(ticket, ticket_data.category_ids)

            if ticket_data.label_ids is not None:
                self.repository.update_labels(ticket, ticket_data.label_ids)

            self.db.commit()
            return self.repository.get_with_relations(ticket.id)

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"更新工單失敗: {str(e)}"
            )

    async def update_ticket_status(self, ticket_id: int, status_data: TicketStatusUpdate, current_user_id: int) -> Ticket:
        """更新工單狀態 (後續需要加入狀態機驗證)"""
        ticket = self.repository.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工單不存在"
            )

        # TODO: 加入狀態轉換驗證邏輯
        ticket.status = status_data.status
        ticket.updated_by = current_user_id

        # TODO: 記錄狀態變更到 timeline (ticket_notes)

        self.db.commit()
        return ticket

    def _can_view_ticket(self, ticket: Ticket, user_id: int) -> bool:
        """基礎權限檢查邏輯"""
        # INTERNAL 工單所有人都可以看
        if ticket.visibility == TicketVisibility.INTERNAL:
            return True

        # RESTRICTED 工單只有建立者可以看 (後續會擴展更複雜的權限邏輯)
        if ticket.visibility == TicketVisibility.RESTRICTED:
            return ticket.created_by == user_id

        return False
```### 1.4 建立 Ticket Router 🎯
- **預估時間**: 60 分鐘
- **參考範例**: `app/routers/category_router.py`

#### 具體任務：
- [ ] 建立 `app/routers/ticket_router.py`
- [ ] 實作基本 CRUD API 端點
- [ ] 簡單的身份驗證依賴 (可先用假的 current_user)
- [ ] 基本的錯誤處理

```python
# app/routers/ticket_router.py 預覽
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketStatusUpdate
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])

# TODO: 暫時使用假的用戶依賴，後續需要實作真正的身份驗證
def get_current_user_id() -> int:
    return 1  # 假設當前用戶 ID 為 1

def get_ticket_service(db: Session = Depends(get_db)) -> TicketService:
    return TicketService(db)

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """建立新工單 (支援 template、categories、labels)"""
    created_ticket = await ticket_service.create_ticket(ticket, current_user_id)
    return created_ticket

@router.get("/my", response_model=List[TicketResponse])
async def get_my_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """取得我建立的工單列表"""
    tickets = await ticket_service.get_user_tickets(current_user_id, current_user_id)
    return tickets

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """取得單一工單詳細資訊 (含權限檢查)"""
    ticket = await ticket_service.get_ticket_by_id(ticket_id, current_user_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工單不存在"
        )
    return ticket

@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新工單基本資訊和關聯"""
    updated_ticket = await ticket_service.update_ticket(ticket_id, ticket_update, current_user_id)
    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工單不存在"
        )
    return updated_ticket

@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新工單狀態 (專用端點，後續加入狀態機驗證)"""
    updated_ticket = await ticket_service.update_ticket_status(ticket_id, status_update, current_user_id)
    return updated_ticket

# 後續可新增的端點
# @router.get("/{ticket_id}/timeline", ...)  # 工單時間軸
# @router.post("/{ticket_id}/notes", ...)    # 新增留言
# @router.get("/{ticket_id}/attachments", ...)  # 工單附件
```

### 1.5 整合 Router 到 Main App 🔗
- **預估時間**: 15 分鐘

#### 具體任務：
- [ ] 在 `app/main.py` 中註冊 `ticket_router`
- [ ] 確保 API 路由正常運作

## 階段二：基本測試 (第一天下午)

### 2.1 手動 API 測試 🧪
- **預估時間**: 30 分鐘

#### 具體任務：
- [ ] 啟動 FastAPI 伺服器
- [ ] 使用 Swagger UI 測試基本 CRUD
- [ ] 驗證資料庫記錄正確建立

### 2.2 簡單單元測試 ✅
- **預估時間**: 45 分鐘
- **參考範例**: `tests/test_category_service.py`

#### 具體任務：
- [ ] 建立 `tests/test_ticket_service.py`
- [ ] 建立 `tests/test_ticket_repository.py`
- [ ] 基本的建立和查詢測試

## 階段三：狀態管理 (第二天)

### 3.1 狀態轉換 API 🔄
- **預估時間**: 2 小時

#### 具體任務：
- [ ] 在 `TicketService` 中加入狀態轉換邏輯
- [ ] 新增 `PATCH /tickets/{id}/status` API 端點
- [ ] 基本的狀態轉換驗證 (如：draft → waiting_approval)

### 3.2 簡單的 Timeline 📜
- **預估時間**: 1.5 小時

#### 具體任務：
- [ ] 實作基本的系統事件記錄 (狀態變更)
- [ ] 新增 `GET /tickets/{id}/timeline` API
- [ ] 簡單的事件顯示

## 階段四：進階功能 (第三天以後)

### 4.1 Category 和 Label 關聯
- [ ] Ticket 與 Category, Label 的關聯管理
- [ ] API 端點支援

### 4.2 基本權限控制
- [ ] 實作 `visibility` 欄位的權限檢查
- [ ] INTERNAL vs RESTRICTED 的基本邏輯

### 4.3 簽核功能 (進階)
- [ ] 基於現有 approval_* 表的簽核流程
- [ ] 簽核 API 端點

## 立即行動計劃 🚀

**現在就開始第一步**：建立 Ticket Schema

請確認是否要立即開始實作 `app/schemas/ticket.py`？
