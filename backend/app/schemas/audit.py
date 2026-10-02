from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None = None
    action: str
    entity_type: str
    entity_id: str
    details: str
    created_at: datetime

    model_config = {"from_attributes": True}
