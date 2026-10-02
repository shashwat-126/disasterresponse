from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.assignment import IncidentAssignment
from app.models.department import Department
from app.models.incident import Incident
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentRead
from app.schemas.incident import IncidentRead
from app.services.assignment_service import serialize_assignment
from app.services.audit_service import log_action

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Department).order_by(Department.name).all()


@router.post("", response_model=DepartmentRead)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    existing = db.query(Department).filter(Department.code == payload.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department code already exists")
    department = Department(
        name=payload.name,
        code=payload.code.upper(),
        category=payload.category.upper(),
        contact_phone=payload.contact_phone,
        contact_email=payload.contact_email,
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    log_action(db, current_user.id, "DEPARTMENT_CREATED", "department", str(department.id), department.name)
    return department


@router.get("/{department_id}/incidents", response_model=list[IncidentRead])
def department_incidents(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "DEPARTMENT_STAFF" and current_user.department_id != department_id:
        raise HTTPException(status_code=403, detail="You can only view incidents for your own department")

    incident_ids = (
        db.query(IncidentAssignment.incident_id)
        .filter(IncidentAssignment.department_id == department_id)
        .subquery()
    )
    return (
        db.query(Incident)
        .filter(Incident.id.in_(incident_ids))
        .order_by(Incident.created_at.desc())
        .all()
    )


@router.get("/{department_id}/workload")
def department_workload(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grouped view for a department's dashboard: what's pending (assigned/acknowledged),
    what's actively in progress, and what's already completed — so staff don't have to
    scroll a flat incident list to find their queue."""
    if current_user.role == "DEPARTMENT_STAFF" and current_user.department_id != department_id:
        raise HTTPException(status_code=403, detail="You can only view your own department's workload")

    assignments = (
        db.query(IncidentAssignment)
        .filter(IncidentAssignment.department_id == department_id)
        .order_by(IncidentAssignment.assigned_at.desc())
        .all()
    )

    def _with_incident_summary(assignment: IncidentAssignment) -> dict:
        payload = serialize_assignment(assignment)
        incident = assignment.incident
        payload["incident"] = {
            "id": incident.id,
            "title": incident.title,
            "location": incident.location,
            "disaster_type": incident.disaster_type,
            "severity": incident.severity,
            "status": incident.status,
            "priority_level": incident.priority_level,
        }
        return payload

    pending = [_with_incident_summary(a) for a in assignments if a.status in ("ASSIGNED", "ACKNOWLEDGED")]
    in_progress = [_with_incident_summary(a) for a in assignments if a.status == "IN_PROGRESS"]
    completed = [_with_incident_summary(a) for a in assignments if a.status == "COMPLETED"]

    return {
        "department_id": department_id,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "counts": {"pending": len(pending), "in_progress": len(in_progress), "completed": len(completed)},
    }
