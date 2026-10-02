
import math
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.incident import Incident

# Two reports of the same disaster_type within this radius and time window are flagged.
DUPLICATE_RADIUS_KM = 2.0
DUPLICATE_WINDOW_HOURS = 6
OPEN_STATUSES = {"SUBMITTED", "TRIAGED", "DISPATCHED", "IN_PROGRESS"}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def find_possible_duplicate(db: Session, incident: Incident) -> Incident | None:
    """Return the best-matching open incident this one is likely a duplicate of, or None."""
    if incident.latitude is None or incident.longitude is None:
        return None

    since = datetime.utcnow() - timedelta(hours=DUPLICATE_WINDOW_HOURS)
    candidates = (
        db.query(Incident)
        .filter(
            Incident.id != incident.id,
            Incident.disaster_type == incident.disaster_type,
            Incident.status.in_(OPEN_STATUSES),
            Incident.created_at >= since,
            Incident.latitude.isnot(None),
            Incident.longitude.isnot(None),
        )
        .all()
    )

    best: Incident | None = None
    best_distance = DUPLICATE_RADIUS_KM
    for candidate in candidates:
        distance = _haversine_km(incident.latitude, incident.longitude, candidate.latitude, candidate.longitude)
        if distance <= best_distance:
            best = candidate
            best_distance = distance
    return best
