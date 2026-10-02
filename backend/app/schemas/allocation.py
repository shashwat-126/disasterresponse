from datetime import datetime

from pydantic import BaseModel


class AllocationRead(BaseModel):
    id: int
    incident_id: int
    ambulances: int
    rescue_teams: int
    vehicles: int
    food_kits: int
    water_liters: int
    shelters: int
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}
