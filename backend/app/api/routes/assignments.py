import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.action_report import ActionReport
from app.models.assignment import IncidentAssignment
from app.models.department import Department
from app.models.incident import Incident
from app.models.user import User
from app.schemas.assignment import AssignmentRead
from app.services.assignment_service import (
    acknowledge_assignment,
    add_extra_assignment,
    complete_assignment,
    reassign_assignment,
    remove_assignment,
    serialize_assignment,
    start_assignment,
)
from app.services.audit_service import log_action
from app.services.file_service import save_proof_files
from app.services.notification_service import (
    notify_assignment_completed,
    notify_extra_department_assigned,
    notify_reassignment,
)

router = APIRouter(tags=["assignments"])


def _get_assignment_or_404(db: Session, assignment_id: int) -> IncidentAssignment:
    assignment = db.query(IncidentAssignment).filter(IncidentAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


def _authorize_department_action(current_user: User, assignment: IncidentAssignment) -> None:
    if current_user.role == "ADMIN":
        return
    if current_user.role == "DEPARTMENT_STAFF" and current_user.department_id == assignment.department_id:
        return
    raise HTTPException(status_code=403, detail="You are not authorized to act on this department's assignment")


@router.get("/incidents/{incident_id}/assignments", response_model=list[AssignmentRead])
def list_incident_assignments(
    incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    assignments = (
        db.query(IncidentAssignment).filter(IncidentAssignment.incident_id == incident_id).all()
    )
    return [serialize_assignment(a) for a in assignments]


@router.post("/assignments/{assignment_id}/acknowledge", response_model=AssignmentRead)
def acknowledge(assignment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assignment = _get_assignment_or_404(db, assignment_id)
    _authorize_department_action(current_user, assignment)
    assignment = acknowledge_assignment(db, assignment)
    log_action(db, current_user.id, "ASSIGNMENT_ACKNOWLEDGED", "assignment", str(assignment.id))
    return serialize_assignment(assignment)


@router.post("/assignments/{assignment_id}/start", response_model=AssignmentRead)
def start(assignment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assignment = _get_assignment_or_404(db, assignment_id)
    _authorize_department_action(current_user, assignment)
    assignment = start_assignment(db, assignment)
    log_action(db, current_user.id, "ASSIGNMENT_STARTED", "assignment", str(assignment.id))
    return serialize_assignment(assignment)


@router.post("/assignments/{assignment_id}/action-report", response_model=AssignmentRead)
def submit_action_report(
    assignment_id: int,
    officer_name: str = Form(...),
    action_taken: str = Form(...),
    team_members: str = Form(""),
    resources_used: str = Form(""),
    remarks: str = Form(""),
    arrival_time: str | None = Form(None),
    completion_time: str | None = Form(None),
    proof_files: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = _get_assignment_or_404(db, assignment_id)
    _authorize_department_action(current_user, assignment)

    if assignment.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="This department has already completed its action report")

    stored_paths = save_proof_files(assignment_id, [f for f in proof_files if f and f.filename])

    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    report = ActionReport(
        assignment_id=assignment.id,
        officer_name=officer_name,
        team_members=team_members,
        resources_used=resources_used,
        arrival_time=_parse_dt(arrival_time),
        completion_time=_parse_dt(completion_time) or datetime.utcnow(),
        action_taken=action_taken,
        remarks=remarks,
        proof_file_paths=json.dumps(stored_paths),
    )
    db.add(report)
    db.commit()

    assignment = complete_assignment(db, assignment)
    notify_assignment_completed(db, assignment)
    log_action(
        db,
        current_user.id,
        "ACTION_REPORT_SUBMITTED",
        "assignment",
        str(assignment.id),
        f"proof_files={len(stored_paths)}",
    )
    return serialize_assignment(assignment)


# ---------------------------------------------------------------------------
# Admin coordination: add extra departments, reassign, or drop an assignment.
# These cover real-world cases the automatic rules engine can't foresee — the
# wrong department got pulled in, an incident turns out to need a department
# beyond the initial rule-based set, or a department becomes unavailable.
# ---------------------------------------------------------------------------


def _get_incident_or_404(db: Session, incident_id: int) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


def _get_department_or_404(db: Session, department_id: int) -> Department:
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.post("/incidents/{incident_id}/assignments", response_model=AssignmentRead)
def add_department(
    incident_id: int,
    department_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    incident = _get_incident_or_404(db, incident_id)
    department = _get_department_or_404(db, department_id)
    assignment = add_extra_assignment(db, incident, department)
    notify_extra_department_assigned(db, assignment)
    log_action(
        db, current_user.id, "DEPARTMENT_ADDED", "incident", str(incident_id), f"department={department_id}"
    )
    return serialize_assignment(assignment)


@router.patch("/assignments/{assignment_id}/reassign", response_model=AssignmentRead)
def reassign(
    assignment_id: int,
    department_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    assignment = _get_assignment_or_404(db, assignment_id)
    if assignment.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Cannot reassign a completed assignment")

    new_department = _get_department_or_404(db, department_id)
    old_name = assignment.department.name
    assignment = reassign_assignment(db, assignment, new_department)
    notify_reassignment(db, assignment, old_name)
    log_action(
        db, current_user.id, "ASSIGNMENT_REASSIGNED", "assignment", str(assignment.id),
        f"from={old_name} to={new_department.name}",
    )
    return serialize_assignment(assignment)


@router.delete("/assignments/{assignment_id}")
def remove(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    assignment = _get_assignment_or_404(db, assignment_id)
    if assignment.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Cannot remove a department that already completed its work")

    department_name = assignment.department.name
    incident_id = assignment.incident_id
    remove_assignment(db, assignment)
    log_action(
        db, current_user.id, "DEPARTMENT_REMOVED", "incident", str(incident_id), f"department={department_name}"
    )
    return {"status": "ok"}
