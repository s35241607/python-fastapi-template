from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.services.ticket_service import TicketService
from app.schemas.item import (
    Ticket, TicketCreate, TicketUpdate, CommentCreate,
    TicketWithInitialComment, Comment
)
from app.models.ticket import TicketStatus

router = APIRouter()

@router.post("/tickets/", response_model=Ticket)
async def create_ticket_with_comment(
    data: TicketWithInitialComment,
    db: AsyncSession = Depends(get_db)
):
    service = TicketService(db)
    try:
        ticket = await service.create_ticket_with_initial_comment(
            data.ticket, data.initial_comment
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tickets/", response_model=List[Ticket])
async def read_tickets(db: AsyncSession = Depends(get_db)):
    service = TicketService(db)
    return await service.get_all_tickets_with_details()

@router.get("/tickets/{ticket_id}", response_model=Ticket)
async def read_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    service = TicketService(db)
    ticket = await service.get_ticket_with_details(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/tickets/{ticket_id}/status", response_model=Ticket)
async def update_ticket_status(
    ticket_id: int,
    status: TicketStatus,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = TicketService(db)
    try:
        ticket = await service.update_ticket_status(ticket_id, status, user_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    service = TicketService(db)
    success = await service.delete_ticket_with_comments(ticket_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found or unauthorized")
    return {"message": "Ticket and associated comments deleted"}

@router.post("/tickets/{ticket_id}/comments/", response_model=Comment)
async def add_comment_to_ticket(
    ticket_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db)
):
    service = TicketService(db)
    try:
        return await service.add_comment_to_ticket(ticket_id, comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
