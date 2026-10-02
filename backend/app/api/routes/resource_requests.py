from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.incident import Incident
from app.models.resource_request import ResourceRequest
from app.models.user import User
from app.schemas.resource_request import ResourceRequestCreate, ResourceRequestRead, ResourceRequestResolve
from app.services.audit_service import log_action
from app.services.notification_service import notify_resource_request_created, notify_resource_request_resolved
from app.services.resource_request_service import create_resource_request, resolve_resource_request

router = APIRouter(tags=["resource-requests"])


def _get_incident_or_404(db: Session, incident_id: int) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


def _resolve_department_id(db: Session, incident: Incident, current_user: User, requested_department_id: int | None) -> int:
    if current_user.role == "DEPARTMENT_STAFF":
        department_id = current_user.department_id
    elif current_user.role == "ADMIN":
        if not requested_department_id:
            raise HTTPException(status_code=400, detail="department_id is required when acting as admin")
        department_id = requested_department_id
    else:
        raise HTTPException(status_code=403, detail="Only department staff or admins can do this")

    is_assigned = any(a.department_id == department_id for a in incident.assignments)
    if not is_assigned:
        raise HTTPException(status_code=403, detail="That department is not assigned to this incident")
    return department_id


@router.post("/incidents/{incident_id}/resource-requests", response_model=ResourceRequestRead)
def create_request(
    incident_id: int,
    payload: ResourceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = _get_incident_or_404(db, incident_id)
    department_id = _resolve_department_id(db, incident, current_user, payload.department_id)

    request = create_resource_request(
        db, incident, department_id, current_user, payload.resource_type, payload.quantity, payload.justification
    )
    notify_resource_request_created(db, request)
    log_action(
        db, current_user.id, "RESOURCE_REQUEST_CREATED", "resource_request", str(request.id),
        f"incident={incident_id} type={payload.resource_type} qty={payload.quantity}",
    )
    return request


@router.get("/incidents/{incident_id}/resource-requests", response_model=list[ResourceRequestRead])
def list_incident_requests(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_incident_or_404(db, incident_id)
    return (
        db.query(ResourceRequest)
        .filter(ResourceRequest.incident_id == incident_id)
        .order_by(ResourceRequest.created_at.desc())
        .all()
    )


@router.get("/resource-requests", response_model=list[ResourceRequestRead])
def list_all_requests(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    query = db.query(ResourceRequest)
    if status_filter:
        query = query.filter(ResourceRequest.status == status_filter.upper())
    return query.order_by(ResourceRequest.created_at.desc()).all()


@router.patch("/resource-requests/{request_id}", response_model=ResourceRequestRead)
def resolve_request(
    request_id: int,
    payload: ResourceRequestResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    request = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Resource request not found")

    request = resolve_resource_request(db, request, current_user, payload.status, payload.resolution_notes)
    notify_resource_request_resolved(db, request)
    log_action(db, current_user.id, "RESOURCE_REQUEST_RESOLVED", "resource_request", str(request.id), f"status={request.status}")
    return request
