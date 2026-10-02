from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.incident import Incident
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total = db.query(func.count(Incident.id)).scalar() or 0
    critical = db.query(func.count(Incident.id)).filter(Incident.severity == "CRITICAL").scalar() or 0
    high = db.query(func.count(Incident.id)).filter(Incident.severity == "HIGH").scalar() or 0
    resolved = db.query(func.count(Incident.id)).filter(Incident.status == "RESOLVED").scalar() or 0
    return DashboardSummary(
        total_incidents=total,
        critical_incidents=critical,
        high_incidents=high,
        resolved_incidents=resolved,
    )
