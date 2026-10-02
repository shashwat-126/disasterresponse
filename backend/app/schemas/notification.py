from datetime import datetime

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    incident_id: int | None = None
    notif_type: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    unread_count: int
    notifications: list[NotificationRead]
