from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentDetail, IncidentRead, IncidentStatusUpdate
from app.services.assignment_service import all_assignments_completed, pending_department_names, serialize_assignment
from app.services.audit_service import log_action
from app.services.incident_service import create_incident as create_incident_record
from app.services.notification_service import notify_incident_resolved
from app.services.sla_service import is_breached, sla_target_for

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_incident_record(db, payload, current_user)


@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Incident)
    # Citizens only see their own reports; staff and admins see the full operational queue.
    if current_user.role == "CITIZEN":
        query = query.filter(Incident.created_by == current_user.id)
    return query.order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if current_user.role == "CITIZEN" and incident.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own reports")

    allocation = incident.allocations[-1] if incident.allocations else None
    payload = IncidentRead.model_validate(incident).model_dump()
    payload["allocation"] = allocation
    payload["assignments"] = [serialize_assignment(a) for a in incident.assignments]
    payload["attachments"] = incident.attachments
    payload["ready_to_resolve"] = all_assignments_completed(incident)
    payload["sla_target_minutes"] = sla_target_for(incident.severity)
    payload["sla_breached"] = is_breached(incident)
    payload["resource_requests"] = incident.resource_requests
    payload["damage_updates"] = incident.damage_updates
    return payload


@router.patch("/{incident_id}/status", response_model=IncidentRead)
def update_status(incident_id: int, payload: IncidentStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    new_status = payload.status.upper()
    if new_status == "RESOLVED" and not all_assignments_completed(incident):
        pending = pending_department_names(incident)
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resolve incident: pending action reports from {', '.join(pending) or 'assigned departments'}.",
        )

    incident.status = new_status
    db.commit()
    db.refresh(incident)
    log_action(db, current_user.id, "INCIDENT_STATUS_UPDATED", "incident", str(incident.id), f"status={incident.status}")
    if new_status == "RESOLVED":
        notify_incident_resolved(db, incident)
    return incident
