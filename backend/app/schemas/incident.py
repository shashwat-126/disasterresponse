import json
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.allocation import AllocationRead
from app.schemas.assignment import AssignmentRead
from app.schemas.attachment import AttachmentRead
from app.schemas.damage_update import DamageUpdateRead
from app.schemas.resource_request import ResourceRequestRead


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5)
    disaster_type: str
    location: str
    latitude: float | None = None
    longitude: float | None = None
    people_affected: int = Field(ge=0)
    injuries: int = Field(ge=0)
    additional_info: str = ""


class IncidentStatusUpdate(BaseModel):
    status: str


def _parse_json_list(value):
    if isinstance(value, str):
        try:
            return json.loads(value or "[]")
        except (TypeError, ValueError):
            return []
    return value or []


class IncidentRead(BaseModel):
    id: int
    title: str
    description: str
    disaster_type: str
    location: str
    latitude: float | None = None
    longitude: float | None = None
    people_affected: int
    injuries: int
    status: str
    severity: str
    prediction_confidence: float
    model_version: str
    risk_score: float
    priority_level: str
    estimated_response_minutes: int
    secondary_hazards: list[str] = []
    immediate_recommendations: list[str] = []
    explanation_summary: str = ""
    top_signals: list[str] = []
    additional_info: str = ""
    possible_duplicate_of: int | None = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("secondary_hazards", "immediate_recommendations", "top_signals", mode="before")
    @classmethod
    def _parse_lists(cls, value):
        return _parse_json_list(value)


class IncidentDetail(IncidentRead):
    allocation: AllocationRead | None = None
    assignments: list[AssignmentRead] = []
    attachments: list[AttachmentRead] = []
    ready_to_resolve: bool = False
    sla_target_minutes: int | None = None
    sla_breached: bool = False
    resource_requests: list[ResourceRequestRead] = []
    damage_updates: list[DamageUpdateRead] = []
