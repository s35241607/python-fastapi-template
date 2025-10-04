from pydantic import BaseModel, ConfigDict


class TicketViewPermissionRead(BaseModel):
    user_id: int | None = None
    role_id: int | None = None

    model_config = ConfigDict(from_attributes=True)