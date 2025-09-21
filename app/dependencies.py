from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.attachment_service import AttachmentService
from app.services.category_service import CategoryService
from app.services.ticket_service import TicketService


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_attachment_service(db: AsyncSession = Depends(get_db)) -> AttachmentService:
    attachment_repository = AttachmentRepository(db)
    return AttachmentService(attachment_repository)


def get_ticket_repository(db: AsyncSession = Depends(get_db)) -> TicketRepository:
    return TicketRepository(db)


def get_ticket_service(db: AsyncSession = Depends(get_db)) -> TicketService:
    ticket_repository = TicketRepository(db)
    return TicketService(ticket_repository)
