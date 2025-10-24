from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user_id_from_jwt
from app.schemas.response import PaginationResponse
from app.schemas.ticket import (
    TicketAssigneeUpdate,
    TicketCreate,
    TicketDescriptionUpdate,
    TicketLabelsUpdate,
    TicketQueryParams,
    TicketRead,
    TicketTitleUpdate,
    TicketUpdate,
)
from app.services.ticket_service import TicketService

router = APIRouter()


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """建立新工單 (支援 template、categories、labels)"""
    created_ticket = await ticket_service.create_ticket(ticket, current_user_id)
    return created_ticket


@router.get("/", response_model=PaginationResponse[TicketRead])
async def get_tickets(
    query: TicketQueryParams = Depends(),
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> PaginationResponse[TicketRead]:
    """取得工單列表"""
    page_result = await ticket_service.get_tickets(query, current_user_id)
    return page_result


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket_by_id(
    ticket_id: int,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """以 id 取得單一工單"""
    return await ticket_service.get_ticket_by_id(ticket_id, current_user_id)


@router.get("/by-ticket-no/{ticket_no}", response_model=TicketRead)
async def get_ticket_by_ticket_no(
    ticket_no: str,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """以 ticket_no 取得單一工單"""
    return await ticket_service.get_ticket_by_ticket_no(ticket_no, current_user_id)


@router.patch("/{ticket_id}", response_model=TicketRead, status_code=status.HTTP_200_OK)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """部分更新工單

    - 僅票據建立者可編輯
    - 支援部分更新：title, description, priority, visibility, due_date, assigned_to, custom_fields_data, categories, labels
    - 只需提供要修改的欄位，未提供的欄位保持不變
    - 不支援透過此 endpoint 更改 status（需使用狀態轉換 endpoint）

    **Errors:**
    - 404: Ticket not found
    - 403: Unauthorized (non-creator)
    """

    return await ticket_service.update_ticket(ticket_id, ticket_update, current_user_id)


@router.patch("/{ticket_id}/title", response_model=TicketRead, status_code=status.HTTP_200_OK)
async def update_ticket_title(
    ticket_id: int,
    ticket_title_update: TicketTitleUpdate,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """更新工單標題

    **Errors:**
    - 404: Ticket not found
    - 403: Unauthorized (non-creator)
    """
    return await ticket_service.update_ticket_title(ticket_id, ticket_title_update, current_user_id)


@router.patch("/{ticket_id}/description", response_model=TicketRead, status_code=status.HTTP_200_OK)
async def update_ticket_description(
    ticket_id: int,
    ticket_description_update: TicketDescriptionUpdate,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """更新工單描述

    **Errors:**
    - 404: Ticket not found
    - 403: Unauthorized (non-creator)
    """
    return await ticket_service.update_ticket_description(ticket_id, ticket_description_update, current_user_id)


@router.patch("/{ticket_id}/assignee", response_model=TicketRead, status_code=status.HTTP_200_OK)
async def update_ticket_assignee(
    ticket_id: int,
    ticket_assignee_update: TicketAssigneeUpdate,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """更新工單指派對象

    **Errors:**
    - 404: Ticket not found
    - 403: Unauthorized (non-creator)
    """
    return await ticket_service.update_ticket_assignee(ticket_id, ticket_assignee_update, current_user_id)


@router.patch("/{ticket_id}/labels", response_model=TicketRead, status_code=status.HTTP_200_OK)
async def update_ticket_labels(
    ticket_id: int,
    ticket_labels_update: TicketLabelsUpdate,
    ticket_service: TicketService = Depends(TicketService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> TicketRead:
    """更新工單標籤

    **Errors:**
    - 404: Ticket not found
    - 403: Unauthorized (non-creator)
    """
    return await ticket_service.update_ticket_labels(ticket_id, ticket_labels_update, current_user_id)


# @router.get("/{ticket_id}", response_model=TicketRead)


# @router.put("/{ticket_id}", response_model=TicketRead)


# @router.patch("/{ticket_id}/status", response_model=TicketRead)


# 後續可新增的端點
# @router.get("/{ticket_id}/timeline", ...)  # 工單時間軸
# @router.post("/{ticket_id}/notes", ...)    # 新增留言
# @router.get("/{ticket_id}/attachments", ...)  # 工單附件
