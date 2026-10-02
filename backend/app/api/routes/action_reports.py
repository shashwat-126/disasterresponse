import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, require_roles
from app.models.action_report import ActionReport
from app.models.assignment import IncidentAssignment
from app.models.incident import Incident
from app.models.user import User

router = APIRouter(prefix="/action-reports", tags=["action-reports"])


@router.get("")
def list_action_reports(
    department_id: int | None = None,
    disaster_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    """Admin-only, cross-incident view of every action report departments have filed —
    including their proof files. Individual incident pages already show a department's
    report in context; this exists for the case an admin needs to audit or search across
    *all* of them (e.g. "show me everything Fire filed this month") without opening each
    incident one at a time.
    """
    query = (
        db.query(ActionReport)
        .join(IncidentAssignment, ActionReport.assignment_id == IncidentAssignment.id)
        .join(Incident, IncidentAssignment.incident_id == Incident.id)
        .options(
            joinedload(ActionReport.assignment).joinedload(IncidentAssignment.department),
            joinedload(ActionReport.assignment).joinedload(IncidentAssignment.incident),
        )
    )
    if department_id:
        query = query.filter(IncidentAssignment.department_id == department_id)
    if disaster_type:
        query = query.filter(Incident.disaster_type == disaster_type.upper())

    reports = query.order_by(ActionReport.created_at.desc()).all()

    results = []
    for report in reports:
        assignment = report.assignment
        incident = assignment.incident
        try:
            proof_paths = json.loads(report.proof_file_paths or "[]")
        except (TypeError, ValueError):
            proof_paths = []
        results.append(
            {
                "id": report.id,
                "assignment_id": assignment.id,
                "incident_id": incident.id,
                "incident_title": incident.title,
                "incident_location": incident.location,
                "disaster_type": incident.disaster_type,
                "severity": incident.severity,
                "department": {
                    "id": assignment.department.id,
                    "name": assignment.department.name,
                    "code": assignment.department.code,
                },
                "officer_name": report.officer_name,
                "team_members": report.team_members,
                "resources_used": report.resources_used,
                "action_taken": report.action_taken,
                "remarks": report.remarks,
                "arrival_time": report.arrival_time,
                "completion_time": report.completion_time,
                "proof_file_paths": proof_paths,
                "created_at": report.created_at,
            }
        )
    return results
