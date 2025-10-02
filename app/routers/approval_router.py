from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user_id_from_jwt
from app.schemas.approval import ApprovalAction, ApprovalProcessRead
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])


def get_approval_service(approval_service: ApprovalService = Depends(ApprovalService)) -> ApprovalService:
    return approval_service


@router.post(
    "/process-steps/{step_id}/approve",
    response_model=ApprovalProcessRead,
    status_code=status.HTTP_200_OK,
)
async def approve_approval_step(
    step_id: int,
    action: ApprovalAction,
    approval_service: ApprovalService = Depends(get_approval_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """核准一個簽核步驟"""
    updated_process = await approval_service.approve_step(
        step_id=step_id, action=action, current_user_id=current_user_id
    )
    return updated_process


@router.post(
    "/process-steps/{step_id}/reject",
    response_model=ApprovalProcessRead,
    status_code=status.HTTP_200_OK,
)
async def reject_approval_step(
    step_id: int,
    action: ApprovalAction,
    approval_service: ApprovalService = Depends(get_approval_service),
    current_user_id: int = Depends(get_user_id_from_jwt),
):
    """駁回一個簽核步驟"""
    updated_process = await approval_service.reject_step(
        step_id=step_id, action=action, current_user_id=current_user_id
    )
    return updated_process