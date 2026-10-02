from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.attachment import IncidentAttachment
from app.models.incident import Incident
from app.models.user import User
from app.schemas.attachment import AttachmentRead
from app.services.audit_service import log_action
from app.services.file_service import classify_file, save_incident_attachments

router = APIRouter(prefix="/incidents", tags=["attachments"])


@router.post("/{incident_id}/attachments", response_model=list[AttachmentRead])
def upload_attachments(
    incident_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if current_user.role == "CITIZEN" and incident.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only attach media to your own reports")

    valid_files = [f for f in files if f and f.filename]
    if not valid_files:
        raise HTTPException(status_code=400, detail="No valid files provided")

    stored_paths = save_incident_attachments(incident_id, valid_files)
    created: list[IncidentAttachment] = []
    for path, upload in zip(stored_paths, valid_files):
        attachment = IncidentAttachment(
            incident_id=incident_id,
            file_path=path,
            file_type=classify_file(upload.filename),
            uploaded_by=current_user.id,
        )
        db.add(attachment)
        created.append(attachment)
    db.commit()
    for attachment in created:
        db.refresh(attachment)

    log_action(db, current_user.id, "ATTACHMENTS_UPLOADED", "incident", str(incident_id), f"count={len(created)}")
    return created


@router.get("/{incident_id}/attachments", response_model=list[AttachmentRead])
def list_attachments(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if current_user.role == "CITIZEN" and incident.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view attachments on your own reports")
    return incident.attachments
