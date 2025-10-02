from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import (
    ApprovalProcess,
    ApprovalProcessStep,
    ApprovalTemplate,
    ApprovalTemplateStep,
)
from app.repositories.base_repository import BaseRepository
from app.schemas.approval import ApprovalProcessRead, ApprovalTemplateRead


class ApprovalProcessRepository(BaseRepository[ApprovalProcess, ApprovalProcess, ApprovalProcess, ApprovalProcessRead]):
    model = ApprovalProcess

    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(session, schema=ApprovalProcessRead)


class ApprovalProcessStepRepository(BaseRepository[ApprovalProcessStep, ApprovalProcessStep, ApprovalProcessStep, ApprovalProcessRead]):
    model = ApprovalProcessStep

    def __init__(self, session: AsyncSession = Depends(get_db)):
        # Note: Using ApprovalProcessRead for the step repo is not ideal, but we don't have a specific StepRead schema yet
        # that isn't part of the main process. This is acceptable for now.
        super().__init__(session, schema=None, auto_convert=False)  # We will handle conversion manually if needed


class ApprovalTemplateRepository(BaseRepository[ApprovalTemplate, ApprovalTemplate, ApprovalTemplate, ApprovalTemplateRead]):
    model = ApprovalTemplate

    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(session, schema=ApprovalTemplateRead)


class ApprovalTemplateStepRepository(
    BaseRepository[ApprovalTemplateStep, ApprovalTemplateStep, ApprovalTemplateStep, ApprovalTemplateRead]
):
    model = ApprovalTemplateStep

    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(session, schema=None, auto_convert=False)