from pydantic import BaseModel, ConfigDict


class NotificationRuleRead(BaseModel):
    id: int
    notify_on_event: str

    model_config = ConfigDict(from_attributes=True)


class NotificationRuleCreate(BaseModel):
    ticket_template_id: int | None = None
    ticket_id: int | None = None
    notify_on_event: str
    user_ids: list[int] = []
    role_ids: list[int] = []


class NotificationRuleUpdate(BaseModel):
    user_ids: list[int] | None = None
    role_ids: list[int] | None = None