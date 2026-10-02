from datetime import datetime

from pydantic import BaseModel


class ActionReportCreate(BaseModel):
    officer_name: str
    team_members: str = ""
    resources_used: str = ""
    arrival_time: datetime | None = None
    completion_time: datetime | None = None
    action_taken: str
    remarks: str = ""


class ActionReportRead(BaseModel):
    id: int
    assignment_id: int
    officer_name: str
    team_members: str
    resources_used: str
    arrival_time: datetime | None = None
    completion_time: datetime | None = None
    action_taken: str
    remarks: str
    proof_file_paths: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}
