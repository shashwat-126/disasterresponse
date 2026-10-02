from sqlalchemy.orm import Session

from app.models.assignment import IncidentAssignment
from app.models.incident import Incident
from app.models.notification import Notification
from app.models.user import User


def _create(db: Session, user_id: int, message: str, incident_id: int | None, notif_type: str) -> Notification:
    notification = Notification(user_id=user_id, incident_id=incident_id, message=message, notif_type=notif_type)
    db.add(notification)
    return notification


def _admin_ids(db: Session) -> list[int]:
    return [u.id for u in db.query(User).filter(User.role == "ADMIN").all()]


def notify_incident_created(db: Session, incident: Incident) -> None:
    message = f"Incident #{incident.id} '{incident.title}' reported ({incident.severity}) and assigned to responding departments."
    for admin_id in _admin_ids(db):
        _create(db, admin_id, message, incident.id, "INCIDENT_CREATED")
    _create(
        db,
        incident.created_by,
        f"Your report '{incident.title}' was received. AI assessed severity: {incident.severity}.",
        incident.id,
        "INCIDENT_CREATED",
    )
    for assignment in incident.assignments:
        for staff in db.query(User).filter(User.department_id == assignment.department_id).all():
            _create(
                db,
                staff.id,
                f"New incident #{incident.id} assigned to {assignment.department.name}: '{incident.title}' ({incident.severity}).",
                incident.id,
                "DEPARTMENT_ASSIGNED",
            )
    db.commit()


def notify_assignment_completed(db: Session, assignment: IncidentAssignment) -> None:
    incident = assignment.incident
    message = f"{assignment.department.name} completed its response for incident #{incident.id} '{incident.title}'."
    for admin_id in _admin_ids(db):
        _create(db, admin_id, message, incident.id, "DEPARTMENT_COMPLETED")
    _create(
        db,
        incident.created_by,
        f"Update on your report '{incident.title}': {assignment.department.name} has completed its response.",
        incident.id,
        "DEPARTMENT_COMPLETED",
    )
    db.commit()


def notify_department_staff(db: Session, department_id: int, message: str, incident_id: int | None, notif_type: str) -> None:
    for staff in db.query(User).filter(User.department_id == department_id).all():
        _create(db, staff.id, message, incident_id, notif_type)
    db.commit()


def notify_extra_department_assigned(db: Session, assignment: IncidentAssignment) -> None:
    incident = assignment.incident
    notify_department_staff(
        db,
        assignment.department_id,
        f"You've been added to incident #{incident.id} '{incident.title}' by an admin.",
        incident.id,
        "DEPARTMENT_ASSIGNED",
    )
    for admin_id in _admin_ids(db):
        _create(
            db,
            admin_id,
            f"{assignment.department.name} added to incident #{incident.id} '{incident.title}'.",
            incident.id,
            "DEPARTMENT_ASSIGNED",
        )
    db.commit()


def notify_reassignment(db: Session, assignment: IncidentAssignment, old_department_name: str) -> None:
    incident = assignment.incident
    notify_department_staff(
        db,
        assignment.department_id,
        f"Incident #{incident.id} '{incident.title}' was reassigned to your department (previously {old_department_name}).",
        incident.id,
        "DEPARTMENT_ASSIGNED",
    )
    db.commit()


def notify_resource_request_created(db: Session, request) -> None:
    incident = request.incident
    message = (
        f"{request.department.name} requested {request.quantity} x {request.resource_type} "
        f"for incident #{incident.id} '{incident.title}'."
    )
    for admin_id in _admin_ids(db):
        _create(db, admin_id, message, incident.id, "RESOURCE_REQUEST_CREATED")
    db.commit()


def notify_resource_request_resolved(db: Session, request) -> None:
    incident = request.incident
    message = (
        f"Your request for {request.quantity} x {request.resource_type} on incident #{incident.id} "
        f"was {request.status.lower()}."
    )
    notify_department_staff(db, request.department_id, message, incident.id, "RESOURCE_REQUEST_RESOLVED")
    db.commit()


def notify_damage_update(db: Session, update) -> None:
    incident = update.incident
    message = (
        f"{update.department.name} posted a damage assessment update on incident #{incident.id} "
        f"'{incident.title}': {update.description[:140]}"
    )
    for admin_id in _admin_ids(db):
        _create(db, admin_id, message, incident.id, "DAMAGE_UPDATE")
    _create(db, incident.created_by, message, incident.id, "DAMAGE_UPDATE")
    for assignment in incident.assignments:
        if assignment.department_id == update.department_id:
            continue
        notify_department_staff(db, assignment.department_id, message, incident.id, "DAMAGE_UPDATE")
    db.commit()


def notify_possible_duplicate(db: Session, incident: Incident, original: Incident) -> None:
    message = (
        f"Incident #{incident.id} '{incident.title}' looks like it may be a duplicate report "
        f"of #{original.id} '{original.title}' (same type, nearby location, reported recently). Please review."
    )
    for admin_id in _admin_ids(db):
        _create(db, admin_id, message, incident.id, "POSSIBLE_DUPLICATE")
    db.commit()


def notify_incident_resolved(db: Session, incident: Incident) -> None:
    _create(
        db,
        incident.created_by,
        f"Your report '{incident.title}' has been marked RESOLVED. You can download the final report now.",
        incident.id,
        "INCIDENT_RESOLVED",
    )
    for assignment in incident.assignments:
        for staff in db.query(User).filter(User.department_id == assignment.department_id).all():
            _create(
                db,
                staff.id,
                f"Incident #{incident.id} '{incident.title}' has been marked RESOLVED by admin.",
                incident.id,
                "INCIDENT_RESOLVED",
            )
    db.commit()
