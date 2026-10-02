from datetime import datetime

from pydantic import BaseModel


class AttachmentRead(BaseModel):
    id: int
    incident_id: int
    file_path: str
    file_type: str
    uploaded_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
