from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.incident import Incident
from app.models.user import User
from app.services.export_service import generate_incidents_csv
from app.services.report_service import generate_incident_report_pdf

router = APIRouter(tags=["exports"])


@router.get("/incidents/{incident_id}/report")
def download_incident_report(
    incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if current_user.role == "CITIZEN" and incident.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only download reports for your own incidents")

    pdf_bytes = generate_incident_report_pdf(incident)
    filename = f"incident-{incident.id}-report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/incidents-export/csv")
def export_incidents_csv(
    db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "DEPARTMENT_STAFF"))
):
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    csv_content = generate_incidents_csv(incidents)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="incidents_export.csv"'},
    )
