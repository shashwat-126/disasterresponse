from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_incidents: int
    critical_incidents: int
    high_incidents: int
    resolved_incidents: int
