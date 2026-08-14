from datetime import datetime

from pydantic import BaseModel, Field


class UpdateResponse(BaseModel):
    id: int
    content: str | None = None
    created_at: datetime
    is_read: bool
    update_type: str
    user_id: int | None = None
    pin_id: int | None = None
    comment_id: int | None = None
    reply_id: int | None = None
    metadata: dict | None = Field(default=None, validation_alias="meta")

    model_config = {"from_attributes": True, "populate_by_name": True}
