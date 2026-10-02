from sqlalchemy.orm import Session

from app.models.damage_update import DamageUpdate
from app.models.incident import Incident
from app.models.user import User


def create_damage_update(
    db: Session,
    incident: Incident,
    department_id: int,
    user: User,
    description: str,
    revised_people_affected: int | None,
    revised_injuries: int | None,
    severity_reassessment: str | None,
) -> DamageUpdate:
    update = DamageUpdate(
        incident_id=incident.id,
        department_id=department_id,
        reported_by=user.id,
        description=description,
        revised_people_affected=revised_people_affected,
        revised_injuries=revised_injuries,
        severity_reassessment=severity_reassessment,
    )
    db.add(update)

    # Ground truth from a responding department supersedes the citizen's initial estimate —
    # keep the incident's headline numbers current so analytics/allocation stay accurate.
    if revised_people_affected is not None:
        incident.people_affected = revised_people_affected
    if revised_injuries is not None:
        incident.injuries = revised_injuries

    db.commit()
    db.refresh(update)
    return update
