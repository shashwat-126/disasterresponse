from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.department import DepartmentRead


class ResourceRequestCreate(BaseModel):
    resource_type: str = Field(min_length=2, max_length=50)
    quantity: int = Field(gt=0)
    justification: str = Field(min_length=3)
    department_id: int | None = None  # required when the caller is ADMIN acting on behalf of a department


class ResourceRequestResolve(BaseModel):
    status: str  # APPROVED | REJECTED | FULFILLED
    resolution_notes: str = ""


class ResourceRequestRead(BaseModel):
    id: int
    incident_id: int
    department: DepartmentRead
    requested_by: int
    resource_type: str
    quantity: int
    justification: str
    status: str
    resolved_by: int | None = None
    resolution_notes: str
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}
