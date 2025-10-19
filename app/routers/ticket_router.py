from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user_id_from_jwt
from app.schemas.response import PaginationResponse
from app.schemas.ticket import TicketCreate, TicketQueryParams, TicketRead
from app.services.ticket_service import TicketService

router = APIRouter()


def get_ticket_service(ticket_service: TicketService = Depends(TicketService)) -> TicketService:
    return ticket_service


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """建立新工單 (支援 template、categories、labels)"""
    created_ticket = await ticket_service.create_ticket(ticket, current_user_id)
    return created_ticket


@router.get("/", response_model=PaginationResponse[TicketRead])
async def get_tickets(
    query: TicketQueryParams = Depends(),
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> PaginationResponse[TicketRead]:
    """取得工單列表"""
    page_result = await ticket_service.get_tickets(query, current_user_id)
    return page_result


# @router.get("/my", response_model=list[TicketRead])


# @router.get("/{ticket_id}", response_model=TicketRead)


# @router.put("/{ticket_id}", response_model=TicketRead)


# @router.patch("/{ticket_id}/status", response_model=TicketRead)


# 後續可新增的端點
# @router.get("/{ticket_id}/timeline", ...)  # 工單時間軸
# @router.post("/{ticket_id}/notes", ...)    # 新增留言
# @router.get("/{ticket_id}/attachments", ...)  # 工單附件
