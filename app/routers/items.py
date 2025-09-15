from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.item import Item, ItemCreate
from app.models.item import ItemModel

router = APIRouter()

# 模擬資料庫
items_db = []

@router.get("/items/", response_model=List[Item])
async def read_items():
    return items_db

@router.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id >= len(items_db) or item_id < 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@router.post("/items/", response_model=Item)
async def create_item(item: ItemCreate):
    new_item = ItemModel(id=len(items_db), **item.dict())
    items_db.append(new_item)
    return new_item

@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    if item_id >= len(items_db) or item_id < 0:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = ItemModel(id=item_id, **item.dict())
    return items_db[item_id]

@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id >= len(items_db) or item_id < 0:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": "Item deleted"}
