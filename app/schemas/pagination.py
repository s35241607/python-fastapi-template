from typing import Any

from pydantic import BaseModel, Field, field_validator


class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1, description="頁碼")
    page_size: int = Field(20, ge=1, le=200, description="每頁筆數")
    sort_by: str = Field("created_at", description="排序欄位")
    sort_order: str = Field("desc", description="排序方向 asc/desc")

    @classmethod
    def _normalize_sort_order(cls, v: str | None):
        if v is None:
            return "desc"
        low = v.lower()
        return "asc" if low == "asc" else "desc"

    _norm_sort_order = field_validator("sort_order", mode="before", check_fields=False)(_normalize_sort_order)

    def extract_filters(self, *, exclude: set[str] | None = None) -> dict[str, Any]:
        ex = exclude or {"page", "page_size", "sort_by", "sort_order"}
        return self.model_dump(exclude_unset=True, exclude=ex)

    def pagination(self) -> tuple[int, int]:
        return self.page, self.page_size

    def sort(self) -> tuple[str, str]:
        return self.sort_by, self.sort_order
