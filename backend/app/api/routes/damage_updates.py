from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.damage_update import DamageUpdate
from app.models.incident import Incident
from app.models.user import User
from app.schemas.damage_update import DamageUpdateCreate, DamageUpdateRead
from app.services.audit_service import log_action
from app.services.damage_update_service import create_damage_update
from app.services.notification_service import notify_damage_update

router = APIRouter(tags=["damage-updates"])


def _get_incident_or_404(db: Session, incident_id: int) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


def _resolve_department_id(incident: Incident, current_user: User, requested_department_id: int | None) -> int:
    if current_user.role == "DEPARTMENT_STAFF":
        department_id = current_user.department_id
    elif current_user.role == "ADMIN":
        if not requested_department_id:
            raise HTTPException(status_code=400, detail="department_id is required when acting as admin")
        department_id = requested_department_id
    else:
        raise HTTPException(status_code=403, detail="Only department staff or admins can post damage updates")

    is_assigned = any(a.department_id == department_id for a in incident.assignments)
    if not is_assigned:
        raise HTTPException(status_code=403, detail="That department is not assigned to this incident")
    return department_id


@router.post("/incidents/{incident_id}/damage-updates", response_model=DamageUpdateRead)
def create_update(
    incident_id: int,
    payload: DamageUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = _get_incident_or_404(db, incident_id)
    department_id = _resolve_department_id(incident, current_user, payload.department_id)

    update = create_damage_update(
        db,
        incident,
        department_id,
        current_user,
        payload.description,
        payload.revised_people_affected,
        payload.revised_injuries,
        payload.severity_reassessment,
    )
    notify_damage_update(db, update)
    log_action(db, current_user.id, "DAMAGE_UPDATE_POSTED", "incident", str(incident_id), payload.description[:200])
    return update


@router.get("/incidents/{incident_id}/damage-updates", response_model=list[DamageUpdateRead])
def list_updates(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_incident_or_404(db, incident_id)
    return (
        db.query(DamageUpdate)
        .filter(DamageUpdate.incident_id == incident_id)
        .order_by(DamageUpdate.created_at.desc())
        .all()
    )
