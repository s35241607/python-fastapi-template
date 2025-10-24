from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse[T](BaseModel):
    message: str | None = Field(default=None, description="成功訊息，可選")
    data: T | None = Field(default=None, description="響應資料，可選")


class Page[T](BaseModel):
    total: int = Field(..., description="總筆數")
    page: int = Field(..., description="目前頁碼")
    page_size: int = Field(..., description="每頁筆數")
    items: list[T] = Field(default_factory=list, description="分頁項目列表")  # type: ignore


class PaginationResponse[T](BaseModel):
    total: int = Field(..., description="總筆數")
    page: int = Field(..., description="目前頁碼")
    page_size: int = Field(..., description="每頁筆數")
    total_pages: int = Field(..., description="總頁數")
    has_next: bool = Field(..., description="是否有下一頁")
    has_prev: bool = Field(..., description="是否有上一頁")
    items: list[T] = Field(default_factory=list, description="分頁資料")  # type: ignore


class ErrorDetail(BaseModel):
    field: str = Field(description="錯誤欄位名稱")
    message: str = Field(description="錯誤訊息")
    type: str = Field(description="錯誤類型")


class ErrorResponse(BaseModel):
    message: str | None = Field(default=None, description="錯誤總訊息")
    code: int | None = Field(default=None, description="錯誤代碼")
    errors: list[ErrorDetail] | None = Field(default=None, description="詳細錯誤列表")
