from datetime import datetime, timedelta

from app.models.incident import Incident

# SLA targets: minutes allowed from incident creation to resolution, by severity.
SLA_TARGET_MINUTES = {"CRITICAL": 60, "HIGH": 240, "MEDIUM": 720, "LOW": 1440}


def sla_target_for(severity: str) -> int:
    return SLA_TARGET_MINUTES.get((severity or "MEDIUM").upper(), 720)


def is_breached(incident: Incident, now: datetime | None = None) -> bool:
    now = now or datetime.utcnow()
    target = sla_target_for(incident.severity)
    deadline = incident.created_at + timedelta(minutes=target)
    if incident.status == "RESOLVED":
        return incident.updated_at > deadline
    return now > deadline
