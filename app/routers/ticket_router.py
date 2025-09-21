"""
Ticket Router
提供工單相關的 REST API endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_user_id_from_jwt
from app.dependencies import get_ticket_service
from app.schemas.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketSearchParams,
    TicketStatsResponse,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="創建工單",
    description="創建新的工單"
)
async def create_ticket(
    ticket_data: TicketCreate,
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketResponse:
    """創建工單"""
    success, message, ticket = await ticket_service.create_ticket(ticket_data, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ticket


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="獲取工單詳情",
    description="根據工單 ID 獲取工單詳細資訊"
)
async def get_ticket(
    ticket_id: int,
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketResponse:
    """獲取工單詳情"""
    success, message, ticket = await ticket_service.get_ticket(ticket_id, user_id)
    
    if not success:
        if "不存在" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )
    
    return ticket


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="更新工單",
    description="更新工單基本資訊"
)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketResponse:
    """更新工單"""
    success, message, ticket = await ticket_service.update_ticket(
        ticket_id, ticket_data, user_id
    )
    
    if not success:
        if "不存在" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        if "無權限" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ticket


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    summary="更新工單狀態",
    description="更新工單狀態，必須符合狀態轉換規則"
)
async def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketResponse:
    """更新工單狀態"""
    success, message, ticket = await ticket_service.update_ticket_status(
        ticket_id, status_update, user_id
    )
    
    if not success:
        if "不存在" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        if "無權限" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除工單",
    description="軟刪除工單"
)
async def delete_ticket(
    ticket_id: int,
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """刪除工單"""
    success, message = await ticket_service.delete_ticket(ticket_id, user_id)
    
    if not success:
        if "不存在" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        if "無權限" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


@router.get(
    "/",
    response_model=TicketListResponse,
    summary="搜尋工單",
    description="根據條件搜尋工單列表"
)
async def search_tickets(
    # 分頁參數
    page: int = Query(1, ge=1, description="頁碼"),
    size: int = Query(20, ge=1, le=100, description="每頁數量"),
    
    # 搜尋條件
    title: Optional[str] = Query(None, description="標題關鍵字"),
    status: Optional[str] = Query(None, description="狀態（多個用逗號分隔）"),
    priority: Optional[str] = Query(None, description="優先級（多個用逗號分隔）"),
    visibility: Optional[str] = Query(None, description="可見性"),
    assigned_to: Optional[int] = Query(None, description="指派給用戶 ID"),
    created_by: Optional[int] = Query(None, description="創建者用戶 ID"),
    category_ids: Optional[str] = Query(None, description="分類 ID（多個用逗號分隔）"),
    label_ids: Optional[str] = Query(None, description="標籤 ID（多個用逗號分隔）"),
    
    # 用戶認證
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketListResponse:
    """搜尋工單"""
    # 構建搜尋參數
    search_params = TicketSearchParams(
        title=title,
        status=status.split(",") if status else None,
        priority=priority.split(",") if priority else None,
        visibility=visibility,
        assigned_to=assigned_to,
        created_by=created_by,
        category_ids=[int(x) for x in category_ids.split(",")] if category_ids else None,
        label_ids=[int(x) for x in label_ids.split(",")] if label_ids else None,
    )
    
    success, message, result = await ticket_service.search_tickets(
        search_params, user_id, page, size
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return result


@router.get(
    "/stats/summary",
    response_model=TicketStatsResponse,
    summary="獲取工單統計",
    description="獲取用戶可見的工單統計資訊"
)
async def get_ticket_stats(
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketStatsResponse:
    """獲取工單統計"""
    success, message, stats = await ticket_service.get_ticket_stats(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return stats


# 工單號碼查詢端點
@router.get(
    "/by-ticket-no/{ticket_no}",
    response_model=TicketResponse,
    summary="根據工單號碼查詢",
    description="根據工單號碼獲取工單詳情"
)
async def get_ticket_by_no(
    ticket_no: str,
    user_id: int = Depends(get_user_id_from_jwt),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketResponse:
    """根據工單號碼查詢"""
    # 需要在 service 中添加相應方法
    # 這裡暫時通過 repository 直接查詢
    from app.dependencies import get_ticket_repository
    from app.database import get_db
    
    async for db in get_db():
        repo = get_ticket_repository(db)
        ticket = await repo.get_by_ticket_no(ticket_no)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工單不存在"
            )
        
        if not await repo.can_user_access_ticket(ticket.id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限訪問此工單"
            )
        
        ticket_with_relations = await repo.get_with_relations(ticket.id)
        return TicketResponse.model_validate(ticket_with_relations)