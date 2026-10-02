from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.assignment import IncidentAssignment
from app.models.department import Department
from app.models.incident import Incident
from app.models.user import User
from app.services.sla_service import is_breached, sla_target_for

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/distribution")
def distribution(db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "DEPARTMENT_STAFF"))):
    incidents = db.query(Incident).all()
    severity_counts: dict[str, int] = defaultdict(int)
    status_counts: dict[str, int] = defaultdict(int)
    priority_counts: dict[str, int] = defaultdict(int)
    for incident in incidents:
        severity_counts[incident.severity] += 1
        status_counts[incident.status] += 1
        priority_counts[incident.priority_level] += 1
    return {
        "severity": dict(severity_counts),
        "status": dict(status_counts),
        "priority": dict(priority_counts),
        "total": len(incidents),
    }


@router.get("/department-performance")
def department_performance(
    db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "DEPARTMENT_STAFF"))
):
    departments = db.query(Department).order_by(Department.name).all()
    results = []
    for department in departments:
        assignments = (
            db.query(IncidentAssignment).filter(IncidentAssignment.department_id == department.id).all()
        )
        total = len(assignments)
        completed = [a for a in assignments if a.status == "COMPLETED"]
        pending = total - len(completed)

        durations = []
        for a in completed:
            if a.completed_at:
                durations.append((a.completed_at - a.assigned_at).total_seconds() / 60)
        avg_minutes = round(sum(durations) / len(durations), 1) if durations else None

        results.append(
            {
                "department_id": department.id,
                "name": department.name,
                "code": department.code,
                "total_assigned": total,
                "completed": len(completed),
                "pending": pending,
                "completion_rate": round(len(completed) / total * 100, 1) if total else 0.0,
                "avg_completion_minutes": avg_minutes,
            }
        )
    return results


@router.get("/sla")
def sla_overview(db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "DEPARTMENT_STAFF"))):
    incidents = db.query(Incident).filter(Incident.status != "RESOLVED").all()
    now = datetime.utcnow()
    breached = []
    for incident in incidents:
        if is_breached(incident, now):
            breached.append(
                {
                    "id": incident.id,
                    "title": incident.title,
                    "severity": incident.severity,
                    "status": incident.status,
                    "created_at": incident.created_at,
                    "sla_target_minutes": sla_target_for(incident.severity),
                    "minutes_overdue": round((now - incident.created_at).total_seconds() / 60 - sla_target_for(incident.severity), 1),
                }
            )
    breached.sort(key=lambda x: x["minutes_overdue"], reverse=True)
    return {
        "open_incidents": len(incidents),
        "breached_count": len(breached),
        "breached_incidents": breached,
    }


@router.get("/trend")
def trend(days: int = 30, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "DEPARTMENT_STAFF"))):
    since = datetime.utcnow() - timedelta(days=days)
    incidents = db.query(Incident).filter(Incident.created_at >= since).all()
    counts: dict[str, int] = defaultdict(int)
    for incident in incidents:
        day_key = incident.created_at.strftime("%Y-%m-%d")
        counts[day_key] += 1

    series = []
    for i in range(days, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        series.append({"date": day, "count": counts.get(day, 0)})
    return {"days": days, "series": series}
