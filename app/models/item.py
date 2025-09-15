from pydantic import BaseModel
from typing import Optional

class ItemModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
