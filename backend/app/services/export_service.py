import csv
from io import StringIO

from app.models.incident import Incident


def generate_incidents_csv(incidents: list[Incident]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id", "title", "disaster_type", "location", "severity", "priority_level", "risk_score",
            "status", "people_affected", "injuries", "estimated_response_minutes",
            "created_at", "updated_at", "created_by",
        ]
    )
    for incident in incidents:
        writer.writerow(
            [
                incident.id,
                incident.title,
                incident.disaster_type,
                incident.location,
                incident.severity,
                incident.priority_level,
                incident.risk_score,
                incident.status,
                incident.people_affected,
                incident.injuries,
                incident.estimated_response_minutes,
                incident.created_at.isoformat(),
                incident.updated_at.isoformat(),
                incident.created_by,
            ]
        )
    return buffer.getvalue()
