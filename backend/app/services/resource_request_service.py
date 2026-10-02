from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.allocation import Allocation
from app.models.incident import Incident
from app.models.resource_request import ResourceRequest
from app.models.user import User
from app.utils.enums import ResourceRequestStatus

ALLOCATION_FIELDS = {"ambulances", "rescue_teams", "vehicles", "food_kits", "water_liters", "shelters"}


def create_resource_request(
    db: Session, incident: Incident, department_id: int, user: User, resource_type: str, quantity: int, justification: str
) -> ResourceRequest:
    request = ResourceRequest(
        incident_id=incident.id,
        department_id=department_id,
        requested_by=user.id,
        resource_type=resource_type.lower(),
        quantity=quantity,
        justification=justification,
        status=ResourceRequestStatus.PENDING.value,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def resolve_resource_request(
    db: Session, request: ResourceRequest, admin: User, new_status: str, notes: str
) -> ResourceRequest:
    new_status = new_status.upper()
    valid_statuses = {s.value for s in ResourceRequestStatus}
    if new_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status '{new_status}'")
    if request.status != ResourceRequestStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This request has already been resolved")

    request.status = new_status
    request.resolution_notes = notes
    request.resolved_by = admin.id
    request.resolved_at = datetime.utcnow()

    # Approving or fulfilling a request tops up the incident's live allocation figures so the
    # numbers responders see reflect what was actually granted, not just the original AI estimate.
    if new_status in (ResourceRequestStatus.APPROVED.value, ResourceRequestStatus.FULFILLED.value):
        if request.resource_type in ALLOCATION_FIELDS:
            allocation = (
                db.query(Allocation)
                .filter(Allocation.incident_id == request.incident_id)
                .order_by(Allocation.created_at.desc())
                .first()
            )
            if allocation:
                current = getattr(allocation, request.resource_type)
                setattr(allocation, request.resource_type, current + request.quantity)

    db.commit()
    db.refresh(request)
    return request
