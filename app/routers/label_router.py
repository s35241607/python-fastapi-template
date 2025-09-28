from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth.dependencies import get_user_id_from_jwt
from app.schemas.label import LabelCreate, LabelRead, LabelUpdate
from app.services.label_service import LabelService

router = APIRouter(dependencies=[Depends(get_user_id_from_jwt)])


@router.post("/", response_model=LabelRead)
async def create_label(
    label_create: LabelCreate,
    services: LabelService = Depends(LabelService),
    user_id: int = Depends(get_user_id_from_jwt),
) -> LabelRead:
    return await services.create_label(label_create, user_id)


@router.get("/", response_model=list[LabelRead])
async def get_labels(services: LabelService = Depends(LabelService)) -> list[LabelRead]:
    return await services.get_labels()


@router.get("/{label_id}", response_model=LabelRead)
async def get_label(label_id: int, services: LabelService = Depends(LabelService)) -> LabelRead:
    label = await services.get_label(label_id)
    if label is None:
        raise HTTPException(status_code=404, detail="Label not found")
    return label


@router.put("/{label_id}", response_model=LabelRead)
async def update_label(
    label_id: int,
    label_update: LabelUpdate,
    services: LabelService = Depends(LabelService),
    user_id: int = Depends(get_user_id_from_jwt),
) -> LabelRead:
    label = await services.update_label(label_id, label_update, user_id)
    if label is None:
        raise HTTPException(status_code=404, detail="Label not found")
    return label


@router.delete("/{label_id}", status_code=204, response_model=None)
async def soft_delete_label(
    label_id: int, services: LabelService = Depends(LabelService), user_id: int = Depends(get_user_id_from_jwt)
) -> Response:
    if not await services.soft_delete_label(label_id, user_id):
        raise HTTPException(status_code=404, detail="Label not found")
    # On success, return 204 No Content with empty body
    return Response(status_code=204)
