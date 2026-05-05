from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DraftCreate(BaseModel):
    form_type: str


class DraftRead(BaseModel):
    id: UUID
    user_id: UUID
    form_type: str
    form_data: dict
    current_step: int
    last_saved_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class DraftUpdate(BaseModel):
    form_data: dict | None = None
    current_step: int | None = None
