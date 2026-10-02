import json

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import IncidentCreate
from app.services.allocation_service import build_allocation
from app.services.assignment_service import auto_assign_departments
from app.services.audit_service import log_action
from app.services.duplicate_detection_service import find_possible_duplicate
from app.services.ml_client import predict_severity
from app.services.notification_service import notify_incident_created, notify_possible_duplicate


def create_incident(db: Session, payload: IncidentCreate, user: User) -> Incident:
    prediction = predict_severity(
        {
            "disaster_type": payload.disaster_type,
            "people_affected": payload.people_affected,
            "injuries": payload.injuries,
        }
    )

    incident = Incident(
        title=payload.title,
        description=payload.description,
        disaster_type=payload.disaster_type,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        people_affected=payload.people_affected,
        injuries=payload.injuries,
        additional_info=payload.additional_info,
        severity=prediction["severity"],
        prediction_confidence=prediction["confidence"],
        model_version=prediction["model_version"],
        risk_score=prediction["risk_score"],
        priority_level=prediction["priority_level"],
        estimated_response_minutes=prediction["estimated_response_minutes"],
        secondary_hazards=json.dumps(prediction["secondary_hazards"]),
        immediate_recommendations=json.dumps(prediction["immediate_recommendations"]),
        explanation_summary=prediction["explanation_summary"],
        top_signals=json.dumps(prediction["top_signals"]),
        created_by=user.id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    allocation = build_allocation(incident.id, incident.severity, incident.people_affected, incident.risk_score)
    db.add(allocation)
    db.commit()
    db.refresh(incident)

    assigned = auto_assign_departments(db, incident)
    db.refresh(incident)

    duplicate_of = find_possible_duplicate(db, incident)
    if duplicate_of:
        incident.possible_duplicate_of = duplicate_of.id
        db.commit()
        db.refresh(incident)
        log_action(
            db, user.id, "POSSIBLE_DUPLICATE_FLAGGED", "incident", str(incident.id), f"matches={duplicate_of.id}"
        )
        notify_possible_duplicate(db, incident, duplicate_of)

    log_action(db, user.id, "INCIDENT_CREATED", "incident", str(incident.id), f"severity={incident.severity}")
    log_action(
        db,
        user.id,
        "DEPARTMENTS_ASSIGNED",
        "incident",
        str(incident.id),
        f"departments={[a.department_id for a in assigned]}",
    )
    notify_incident_created(db, incident)
    return incident
