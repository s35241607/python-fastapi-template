from pydantic import BaseModel, ConfigDict
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
