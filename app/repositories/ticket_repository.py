"""
Ticket Repository
"""

import secrets
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.category import Category
from app.models.enums import TicketStatus, TicketVisibility
from app.models.label import Label
from app.models.ticket import Ticket, ticket_categories, ticket_labels
from app.repositories.base_repository import BaseRepository
from app.schemas.ticket import TicketCreate, TicketSearchParams, TicketUpdate


class TicketRepository(BaseRepository[Ticket, TicketCreate, TicketUpdate]):
    """Ticket Repository"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Ticket

    def _generate_ticket_no(self) -> str:
        """生成唯一的工單號碼"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = secrets.token_hex(3).upper()
        return f"TK{timestamp}{random_suffix}"

    async def create_ticket(
        self,
        ticket_data: TicketCreate,
        user_id: int
    ) -> Ticket:
        """創建工單"""
        # 生成唯一工單號碼
        ticket_no = self._generate_ticket_no()
        
        # 確保工單號碼唯一
        while await self.get_by_ticket_no(ticket_no):
            ticket_no = self._generate_ticket_no()

        # 創建工單基本資料
        ticket_dict = ticket_data.model_dump(exclude={"category_ids", "label_ids"})
        ticket_dict.update({
            "ticket_no": ticket_no,
            "status": TicketStatus.DRAFT,
            "created_by": user_id,
            "updated_by": user_id,
        })

        ticket = self.model(**ticket_dict)
        self.db.add(ticket)
        await self.db.flush()  # 獲取 ID

        # 添加分類關聯
        if ticket_data.category_ids:
            await self._set_ticket_categories(ticket.id, ticket_data.category_ids)

        # 添加標籤關聯
        if ticket_data.label_ids:
            await self._set_ticket_labels(ticket.id, ticket_data.label_ids)

        await self.db.commit()
        await self.db.refresh(ticket)
        
        # 載入關聯資料
        return await self.get_with_relations(ticket.id)

    async def update_ticket(
        self,
        ticket_id: int,
        ticket_data: TicketUpdate,
        user_id: int
    ) -> Optional[Ticket]:
        """更新工單"""
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            return None

        # 更新基本欄位
        update_dict = ticket_data.model_dump(exclude_unset=True, exclude={"category_ids", "label_ids"})
        if update_dict:
            update_dict["updated_by"] = user_id
            update_dict["updated_at"] = datetime.now()
            
            for key, value in update_dict.items():
                setattr(ticket, key, value)

        # 更新分類關聯
        if ticket_data.category_ids is not None:
            await self._set_ticket_categories(ticket_id, ticket_data.category_ids)

        # 更新標籤關聯
        if ticket_data.label_ids is not None:
            await self._set_ticket_labels(ticket_id, ticket_data.label_ids)

        await self.db.commit()
        await self.db.refresh(ticket)
        
        return await self.get_with_relations(ticket_id)

    async def get_by_ticket_no(self, ticket_no: str) -> Optional[Ticket]:
        """根據工單號碼查詢"""
        query = select(self.model).where(
            and_(
                self.model.ticket_no == ticket_no,
                self.model.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_with_relations(self, ticket_id: int) -> Optional[Ticket]:
        """獲取包含關聯資料的工單"""
        query = select(self.model).where(
            and_(
                self.model.id == ticket_id,
                self.model.deleted_at.is_(None)
            )
        ).options(
            selectinload(self.model.categories),
            selectinload(self.model.labels),
            selectinload(self.model.attachments),
            selectinload(self.model.notes),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def search_tickets(
        self,
        search_params: TicketSearchParams,
        user_id: int,
        page: int = 1,
        size: int = 20,
        include_restricted: bool = False
    ) -> Tuple[List[Ticket], int]:
        """搜尋工單"""
        query = select(self.model).where(self.model.deleted_at.is_(None))

        # 權限過濾
        if not include_restricted:
            query = query.where(
                or_(
                    self.model.visibility == TicketVisibility.INTERNAL,
                    self.model.created_by == user_id,
                    self.model.assigned_to == user_id
                )
            )

        # 搜尋條件
        if search_params.title:
            query = query.where(self.model.title.ilike(f"%{search_params.title}%"))

        if search_params.status:
            query = query.where(self.model.status.in_(search_params.status))

        if search_params.priority:
            query = query.where(self.model.priority.in_(search_params.priority))

        if search_params.visibility:
            query = query.where(self.model.visibility == search_params.visibility)

        if search_params.assigned_to:
            query = query.where(self.model.assigned_to == search_params.assigned_to)

        if search_params.created_by:
            query = query.where(self.model.created_by == search_params.created_by)

        if search_params.due_date_from:
            query = query.where(self.model.due_date >= search_params.due_date_from)

        if search_params.due_date_to:
            query = query.where(self.model.due_date <= search_params.due_date_to)

        if search_params.created_from:
            query = query.where(self.model.created_at >= search_params.created_from)

        if search_params.created_to:
            query = query.where(self.model.created_at <= search_params.created_to)

        # 分類過濾
        if search_params.category_ids:
            query = query.join(ticket_categories).where(
                ticket_categories.c.category_id.in_(search_params.category_ids)
            )

        # 標籤過濾
        if search_params.label_ids:
            query = query.join(ticket_labels).where(
                ticket_labels.c.label_id.in_(search_params.label_ids)
            )

        # 計算總數
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 分頁和排序
        query = query.options(
            selectinload(self.model.categories),
            selectinload(self.model.labels)
        ).order_by(desc(self.model.created_at))
        
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.db.execute(query)
        tickets = result.scalars().all()

        return tickets, total

    async def update_status(
        self,
        ticket_id: int,
        new_status: TicketStatus,
        user_id: int
    ) -> Optional[Ticket]:
        """更新工單狀態"""
        query = update(self.model).where(
            and_(
                self.model.id == ticket_id,
                self.model.deleted_at.is_(None)
            )
        ).values(
            status=new_status,
            updated_by=user_id,
            updated_at=datetime.now()
        )

        await self.db.execute(query)
        await self.db.commit()
        
        return await self.get_with_relations(ticket_id)

    async def get_stats(self, user_id: int) -> Dict:
        """獲取工單統計"""
        # 基本統計查詢
        base_query = select(self.model).where(
            and_(
                self.model.deleted_at.is_(None),
                or_(
                    self.model.visibility == TicketVisibility.INTERNAL,
                    self.model.created_by == user_id,
                    self.model.assigned_to == user_id
                )
            )
        )

        # 總數
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(total_query)
        total = total_result.scalar()

        # 按狀態統計
        status_query = select(
            self.model.status,
            func.count(self.model.id)
        ).where(
            and_(
                self.model.deleted_at.is_(None),
                or_(
                    self.model.visibility == TicketVisibility.INTERNAL,
                    self.model.created_by == user_id,
                    self.model.assigned_to == user_id
                )
            )
        ).group_by(self.model.status)
        
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # 按優先級統計
        priority_query = select(
            self.model.priority,
            func.count(self.model.id)
        ).where(
            and_(
                self.model.deleted_at.is_(None),
                or_(
                    self.model.visibility == TicketVisibility.INTERNAL,
                    self.model.created_by == user_id,
                    self.model.assigned_to == user_id
                )
            )
        ).group_by(self.model.priority)
        
        priority_result = await self.db.execute(priority_query)
        by_priority = {row[0]: row[1] for row in priority_result}

        # 逾期工單數
        overdue_query = select(func.count()).where(
            and_(
                self.model.deleted_at.is_(None),
                self.model.due_date < datetime.now(),
                self.model.status.notin_([TicketStatus.CLOSED, TicketStatus.CANCELLED]),
                or_(
                    self.model.visibility == TicketVisibility.INTERNAL,
                    self.model.created_by == user_id,
                    self.model.assigned_to == user_id
                )
            )
        )
        overdue_result = await self.db.execute(overdue_query)
        overdue = overdue_result.scalar()

        # 指派給我的工單數
        assigned_query = select(func.count()).where(
            and_(
                self.model.deleted_at.is_(None),
                self.model.assigned_to == user_id
            )
        )
        assigned_result = await self.db.execute(assigned_query)
        assigned_to_me = assigned_result.scalar()

        # 我創建的工單數
        created_query = select(func.count()).where(
            and_(
                self.model.deleted_at.is_(None),
                self.model.created_by == user_id
            )
        )
        created_result = await self.db.execute(created_query)
        created_by_me = created_result.scalar()

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "overdue": overdue,
            "assigned_to_me": assigned_to_me,
            "created_by_me": created_by_me,
        }

    async def can_user_access_ticket(self, ticket_id: int, user_id: int) -> bool:
        """檢查用戶是否可以訪問工單"""
        query = select(self.model).where(
            and_(
                self.model.id == ticket_id,
                self.model.deleted_at.is_(None),
                or_(
                    self.model.visibility == TicketVisibility.INTERNAL,
                    self.model.created_by == user_id,
                    self.model.assigned_to == user_id
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    async def _set_ticket_categories(self, ticket_id: int, category_ids: List[int]) -> None:
        """設置工單分類關聯"""
        # 刪除現有關聯
        delete_query = ticket_categories.delete().where(
            ticket_categories.c.ticket_id == ticket_id
        )
        await self.db.execute(delete_query)

        # 添加新關聯
        if category_ids:
            insert_values = [
                {"ticket_id": ticket_id, "category_id": cat_id}
                for cat_id in category_ids
            ]
            insert_query = ticket_categories.insert().values(insert_values)
            await self.db.execute(insert_query)

    async def _set_ticket_labels(self, ticket_id: int, label_ids: List[int]) -> None:
        """設置工單標籤關聯"""
        # 刪除現有關聯
        delete_query = ticket_labels.delete().where(
            ticket_labels.c.ticket_id == ticket_id
        )
        await self.db.execute(delete_query)

        # 添加新關聯
        if label_ids:
            insert_values = [
                {"ticket_id": ticket_id, "label_id": label_id}
                for label_id in label_ids
            ]
            insert_query = ticket_labels.insert().values(insert_values)
            await self.db.execute(insert_query)