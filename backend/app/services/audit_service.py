from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(db: Session, user_id: int | None, action: str, entity_type: str, entity_id: str, details: str = "") -> None:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(entry)
    db.commit()
