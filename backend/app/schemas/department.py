from datetime import datetime

from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    code: str = Field(min_length=2, max_length=50)
    category: str
    contact_phone: str = ""
    contact_email: str = ""


class DepartmentRead(BaseModel):
    id: int
    name: str
    code: str
    category: str
    contact_phone: str
    contact_email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
