import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class LabelBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(min_length=7, max_length=7)
    description: str | None = Field(None, max_length=255)

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be a valid hex color code (e.g., #FF9000)")
        return v


class LabelCreate(LabelBase):
    pass


class LabelUpdate(LabelBase):
    pass


class LabelRead(LabelBase):
    id: int
    created_at: datetime
    created_by: int | None = None
    updated_at: datetime | None = None
    updated_by: int | None = None

    class Config:
        from_attributes = True
