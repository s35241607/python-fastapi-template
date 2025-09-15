from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.models.comment import Comment
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.repositories.comment_repository import CommentRepository
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.schemas.comment import CommentCreate

class TicketService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ticket_repo = TicketRepository(session)
        self.user_repo = UserRepository(session)
        self.comment_repo = CommentRepository(session)

    async def create_ticket_with_initial_comment(
        self, ticket_data: TicketCreate, initial_comment: CommentCreate
    ) -> Ticket:
        # 檢查用戶是否存在
        user = await self.user_repo.get_by_id(ticket_data.user_id)
        if not user:
            raise ValueError("User not found")

        # 創建 ticket
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            status=ticket_data.status or TicketStatus.OPEN,
            user_id=ticket_data.user_id
        )
        ticket = await self.ticket_repo.create(ticket)

        # 創建初始 comment
        comment = Comment(
            content=initial_comment.content,
            ticket_id=ticket.id,
            user_id=initial_comment.user_id
        )
        await self.comment_repo.create(comment)

        # 重新獲取 ticket 包含所有關聯
        return await self.ticket_repo.get_ticket_with_details(ticket.id)

    async def get_ticket_with_details(self, ticket_id: int) -> Optional[Ticket]:
        return await self.ticket_repo.get_ticket_with_details(ticket_id)

    async def get_all_tickets_with_details(self) -> List[Ticket]:
        return await self.ticket_repo.get_all_with_details()

    async def update_ticket_status(
        self, ticket_id: int, status: TicketStatus, user_id: int
    ) -> Optional[Ticket]:
        # 檢查 ticket 存在且屬於用戶
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None
        if ticket.user_id != user_id:
            raise ValueError("Unauthorized to update this ticket")

        # 更新狀態
        updated_ticket = await self.ticket_repo.update(ticket_id, status=status)

        # 如果關閉 ticket，添加系統 comment
        if status == TicketStatus.CLOSED:
            system_comment = Comment(
                content="Ticket has been closed.",
                ticket_id=ticket_id,
                user_id=user_id  # 或系統用戶 ID
            )
            await self.comment_repo.create(system_comment)

        return await self.ticket_repo.get_ticket_with_details(ticket_id)

    async def delete_ticket_with_comments(self, ticket_id: int, user_id: int) -> bool:
        # 檢查 ticket 存在且屬於用戶
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket or ticket.user_id != user_id:
            return False

        # 刪除將通過 cascade 處理 comments
        return await self.ticket_repo.delete(ticket_id)

    async def add_comment_to_ticket(
        self, ticket_id: int, comment_data: CommentCreate
    ) -> Comment:
        # 檢查 ticket 存在
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")

        # 檢查用戶存在
        user = await self.user_repo.get_by_id(comment_data.user_id)
        if not user:
            raise ValueError("User not found")

        comment = Comment(
            content=comment_data.content,
            ticket_id=ticket_id,
            user_id=comment_data.user_id
        )
        return await self.comment_repo.create(comment)
