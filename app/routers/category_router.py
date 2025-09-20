
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_category_service
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("/", response_model=Category)
async def create_category(category: CategoryCreate, services: CategoryService = Depends(get_category_service)):
    return await services.create_category(category)


@router.get("/", response_model=list[Category])
async def read_categories(services: CategoryService = Depends(get_category_service)):
    return await services.get_all_categories()


@router.get("/{category_id}", response_model=Category)
async def read_category(category_id: int, services: CategoryService = Depends(get_category_service)):
    db_category = await services.get_category(category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int, category: CategoryUpdate, services: CategoryService = Depends(get_category_service)
):
    db_category = await services.update_category(category_id, category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@router.delete("/{category_id}", response_model=dict)
async def delete_category(category_id: int, services: CategoryService = Depends(get_category_service)):
    if not await services.delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
