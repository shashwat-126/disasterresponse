from datetime import datetime

from pydantic import BaseModel

from app.schemas.action_report import ActionReportRead
from app.schemas.department import DepartmentRead


class AssignmentRead(BaseModel):
    id: int
    incident_id: int
    department: DepartmentRead
    status: str
    is_lead: bool
    assigned_at: datetime
    acknowledged_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    action_report: ActionReportRead | None = None

    model_config = {"from_attributes": True}


class AssignmentStatusUpdate(BaseModel):
    status: str
