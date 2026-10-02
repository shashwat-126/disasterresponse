from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    department_id: int | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
