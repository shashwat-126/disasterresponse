from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.department import DepartmentRead


class DamageUpdateCreate(BaseModel):
    description: str = Field(min_length=3)
    revised_people_affected: int | None = Field(default=None, ge=0)
    revised_injuries: int | None = Field(default=None, ge=0)
    severity_reassessment: str | None = None
    department_id: int | None = None  # required when the caller is ADMIN acting on behalf of a department


class DamageUpdateRead(BaseModel):
    id: int
    incident_id: int
    department: DepartmentRead
    reported_by: int
    description: str
    revised_people_affected: int | None = None
    revised_injuries: int | None = None
    severity_reassessment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
