from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user_id_from_jwt
from app.schemas.note import TicketNoteCreate, TicketNoteRead
from app.schemas.ticket import (
    TicketCreate,
    TicketRead,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.services.ticket_service import TicketService

router = APIRouter()


def get_ticket_service(ticket_service: TicketService = Depends(TicketService)) -> TicketService:
    return ticket_service


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """建立新工單 (支援 template、categories、labels)"""
    created_ticket = await ticket_service.create_ticket(ticket, current_user_id)
    return created_ticket


@router.get("/", response_model=list[TicketRead])
async def get_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """取得工單列表"""
    tickets = await ticket_service.get_tickets(current_user_id=current_user_id)
    return tickets


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(
    ticket_id: int,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """取得單一工單"""
    ticket = await ticket_service.get_ticket_by_id(ticket_id, current_user_id)
    return ticket


@router.put("/{ticket_id}", response_model=TicketRead)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """更新工單"""
    updated_ticket = await ticket_service.update_ticket(
        ticket_id=ticket_id, ticket_update=ticket_update, current_user_id=current_user_id
    )
    return updated_ticket


@router.patch("/{ticket_id}/status", response_model=TicketRead)
async def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """更新工單狀態"""
    updated_ticket = await ticket_service.update_ticket_status(
        ticket_id=ticket_id, status_update=status_update, current_user_id=current_user_id
    )
    return updated_ticket


@router.get("/{ticket_id}/notes", response_model=list[TicketNoteRead])
async def get_ticket_notes(
    ticket_id: int,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """取得工單的完整時間軸 (留言+系統事件)"""
    notes = await ticket_service.get_ticket_notes(ticket_id=ticket_id, current_user_id=current_user_id)
    return notes


@router.post("/{ticket_id}/notes", response_model=TicketNoteRead, status_code=status.HTTP_201_CREATED)
async def add_ticket_note(
    ticket_id: int,
    note: TicketNoteCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """新增一筆使用者留言"""
    created_note = await ticket_service.add_user_note(
        ticket_id=ticket_id, note_data=note, current_user_id=current_user_id
    )
    return created_note