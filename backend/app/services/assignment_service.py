import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.assignment import IncidentAssignment
from app.models.department import Department
from app.models.incident import Incident
from app.utils.enums import AssignmentStatus, DepartmentCategory

# Base departments always considered for every disaster type, keyed by disaster_type (lowercased).
# Values are DepartmentCategory codes. The DISASTER_MANAGEMENT_AUTHORITY is always attached as the
# coordinating/lead department.
DISASTER_TYPE_RULES: dict[str, list[str]] = {
    "flood": [
        DepartmentCategory.EMERGENCY_RESPONSE,
        DepartmentCategory.MEDICAL,
        DepartmentCategory.FOOD_RELIEF,
        DepartmentCategory.MUNICIPAL,
        DepartmentCategory.WATER_SUPPLY,
    ],
    "fire": [
        DepartmentCategory.FIRE,
        DepartmentCategory.MEDICAL,
        DepartmentCategory.POLICE,
        DepartmentCategory.ELECTRICITY,
    ],
    "earthquake": [
        DepartmentCategory.EMERGENCY_RESPONSE,
        DepartmentCategory.FIRE,
        DepartmentCategory.MEDICAL,
        DepartmentCategory.POLICE,
        DepartmentCategory.MUNICIPAL,
        DepartmentCategory.FOOD_RELIEF,
    ],
    "landslide": [
        DepartmentCategory.EMERGENCY_RESPONSE,
        DepartmentCategory.MEDICAL,
        DepartmentCategory.MUNICIPAL,
        DepartmentCategory.POLICE,
    ],
    "cyclone": [
        DepartmentCategory.EMERGENCY_RESPONSE,
        DepartmentCategory.MEDICAL,
        DepartmentCategory.FOOD_RELIEF,
        DepartmentCategory.ELECTRICITY,
        DepartmentCategory.MUNICIPAL,
    ],
    "industrial_accident": [
        DepartmentCategory.FIRE,
        DepartmentCategory.MEDICAL,
        DepartmentCategory.POLICE,
        DepartmentCategory.ELECTRICITY,
    ],
    "epidemic": [
        DepartmentCategory.MEDICAL,
        DepartmentCategory.MUNICIPAL,
        DepartmentCategory.FOOD_RELIEF,
    ],
}

DEFAULT_RULE = [DepartmentCategory.EMERGENCY_RESPONSE, DepartmentCategory.MEDICAL, DepartmentCategory.POLICE]

# Escalation add-ons layered on top of the base rule when severity is high enough.
SEVERITY_ESCALATION: dict[str, list[str]] = {
    "HIGH": [DepartmentCategory.POLICE, DepartmentCategory.NGO_VOLUNTEERS],
    "CRITICAL": [DepartmentCategory.POLICE, DepartmentCategory.NGO_VOLUNTEERS, DepartmentCategory.ELECTRICITY],
}


def _normalize(category: DepartmentCategory | str) -> str:
    return category.value if isinstance(category, DepartmentCategory) else str(category)


def _categories_for(disaster_type: str, severity: str) -> list[str]:
    key = (disaster_type or "").strip().lower().replace(" ", "_")
    categories = list(DISASTER_TYPE_RULES.get(key, DEFAULT_RULE))
    categories.append(DepartmentCategory.DISASTER_MANAGEMENT_AUTHORITY)
    categories.extend(SEVERITY_ESCALATION.get((severity or "").upper(), []))

    # De-duplicate while preserving order, normalizing enums to their plain string value.
    seen: set[str] = set()
    ordered: list[str] = []
    for category in categories:
        value = _normalize(category)
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def auto_assign_departments(db: Session, incident: Incident) -> list[IncidentAssignment]:
    """Create IncidentAssignment rows for every department relevant to this incident.

    Idempotent: departments already assigned to the incident are skipped.
    """
    categories = _categories_for(incident.disaster_type, incident.severity)
    departments = (
        db.query(Department)
        .filter(Department.category.in_(categories), Department.is_active.is_(True))
        .all()
    )

    existing_department_ids = {a.department_id for a in incident.assignments}
    created: list[IncidentAssignment] = []
    for department in departments:
        if department.id in existing_department_ids:
            continue
        assignment = IncidentAssignment(
            incident_id=incident.id,
            department_id=department.id,
            status=AssignmentStatus.ASSIGNED.value,
            is_lead=(department.category == DepartmentCategory.DISASTER_MANAGEMENT_AUTHORITY.value),
        )
        db.add(assignment)
        created.append(assignment)

    if created:
        db.commit()
        for assignment in created:
            db.refresh(assignment)
    return created


def all_assignments_completed(incident: Incident) -> bool:
    if not incident.assignments:
        return False
    return all(a.status == AssignmentStatus.COMPLETED.value for a in incident.assignments)


def pending_department_names(incident: Incident) -> list[str]:
    return [a.department.name for a in incident.assignments if a.status != AssignmentStatus.COMPLETED.value]


def acknowledge_assignment(db: Session, assignment: IncidentAssignment) -> IncidentAssignment:
    if assignment.status == AssignmentStatus.ASSIGNED.value:
        assignment.status = AssignmentStatus.ACKNOWLEDGED.value
        assignment.acknowledged_at = datetime.utcnow()
        db.commit()
        db.refresh(assignment)
    return assignment


def start_assignment(db: Session, assignment: IncidentAssignment) -> IncidentAssignment:
    if assignment.status in (AssignmentStatus.ASSIGNED.value, AssignmentStatus.ACKNOWLEDGED.value):
        assignment.status = AssignmentStatus.IN_PROGRESS.value
        assignment.started_at = assignment.started_at or datetime.utcnow()
        db.commit()
        db.refresh(assignment)
    return assignment


def complete_assignment(db: Session, assignment: IncidentAssignment) -> IncidentAssignment:
    assignment.status = AssignmentStatus.COMPLETED.value
    assignment.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(assignment)
    return assignment


def add_extra_assignment(db: Session, incident: Incident, department: Department) -> IncidentAssignment:
    """Admin manually attaches an additional department to an incident — e.g. a resource
    request or a damage update revealed a need the auto-assignment rules didn't foresee."""
    existing = next((a for a in incident.assignments if a.department_id == department.id), None)
    if existing:
        return existing
    assignment = IncidentAssignment(
        incident_id=incident.id,
        department_id=department.id,
        status=AssignmentStatus.ASSIGNED.value,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def reassign_assignment(db: Session, assignment: IncidentAssignment, new_department: Department) -> IncidentAssignment:
    """Admin swaps a not-yet-completed assignment to a different department (e.g. the wrong
    department was auto-assigned, or the original one is unavailable). Resets the lifecycle
    so the new department starts fresh from ASSIGNED."""
    assignment.department_id = new_department.id
    assignment.status = AssignmentStatus.ASSIGNED.value
    assignment.acknowledged_at = None
    assignment.started_at = None
    db.commit()
    db.refresh(assignment)
    return assignment


def remove_assignment(db: Session, assignment: IncidentAssignment) -> None:
    """Admin removes a department from an incident. Only allowed before it has completed
    an action report, so completed work is never silently lost."""
    db.delete(assignment)
    db.commit()


def serialize_assignment(assignment: IncidentAssignment) -> dict:
    report = assignment.action_report
    report_payload = None
    if report:
        try:
            proof_paths = json.loads(report.proof_file_paths or "[]")
        except (TypeError, ValueError):
            proof_paths = []
        report_payload = {
            "id": report.id,
            "assignment_id": report.assignment_id,
            "officer_name": report.officer_name,
            "team_members": report.team_members,
            "resources_used": report.resources_used,
            "arrival_time": report.arrival_time,
            "completion_time": report.completion_time,
            "action_taken": report.action_taken,
            "remarks": report.remarks,
            "proof_file_paths": proof_paths,
            "created_at": report.created_at,
        }
    return {
        "id": assignment.id,
        "incident_id": assignment.incident_id,
        "department": assignment.department,
        "status": assignment.status,
        "is_lead": assignment.is_lead,
        "assigned_at": assignment.assigned_at,
        "acknowledged_at": assignment.acknowledged_at,
        "started_at": assignment.started_at,
        "completed_at": assignment.completed_at,
        "action_report": report_payload,
    }
