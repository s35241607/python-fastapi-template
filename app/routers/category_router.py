from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth.dependencies import get_user_id_from_jwt
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(dependencies=[Depends(get_user_id_from_jwt)])


@router.post("/", response_model=CategoryRead)
async def create_category(
    category_create: CategoryCreate,
    services: CategoryService = Depends(CategoryService),
    user_id: int = Depends(get_user_id_from_jwt),
):
    # return the created category directly to match response_model=CategoryRead
    return await services.create_category(category_create, user_id)


@router.get("/", response_model=list[CategoryRead])
async def get_categories(services: CategoryService = Depends(CategoryService)) -> list[CategoryRead]:
    return await services.get_categories()


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, services: CategoryService = Depends(CategoryService)) -> CategoryRead:
    category = await services.get_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    services: CategoryService = Depends(CategoryService),
    user_id: int = Depends(get_user_id_from_jwt),
) -> CategoryRead:
    category = await services.update_category(category_id, category_update, user_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=204, response_model=None)
async def soft_delete_category(
    category_id: int, services: CategoryService = Depends(CategoryService), user_id: int = Depends(get_user_id_from_jwt)
) -> Response:
    if not await services.soft_delete_category(category_id, user_id):
        raise HTTPException(status_code=404, detail="Category not found")
    # On success, return 204 No Content with empty body
    return Response(status_code=204)
