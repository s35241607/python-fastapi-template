from pydantic import BaseModel, Field


class SuccessResponse[T](BaseModel):
    message: str | None = Field(default=None, description="成功訊息，可選")
    data: T | None = Field(default=None, description="響應資料，可選")


class ErrorDetail(BaseModel):
    field: str = Field(description="錯誤欄位名稱")
    message: str = Field(description="錯誤訊息")
    type: str = Field(description="錯誤類型")


class ErrorResponse(BaseModel):
    message: str | None = Field(default=None, description="錯誤總訊息")
    code: int | None = Field(default=None, description="錯誤代碼")
    errors: list[ErrorDetail] | None = Field(default=None, description="詳細錯誤列表")
