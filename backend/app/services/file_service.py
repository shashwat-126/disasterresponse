import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".pdf"}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov"}


def classify_file(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    return "document"


def save_files(category: str, entity_id: int, files: list[UploadFile]) -> list[str]:
    settings = get_settings()
    base_dir = Path(settings.upload_dir) / category / str(entity_id)
    base_dir.mkdir(parents=True, exist_ok=True)

    stored_paths: list[str] = []
    for upload in files:
        if not upload.filename:
            continue
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            continue
        safe_name = f"{uuid.uuid4().hex}{suffix}"
        destination = base_dir / safe_name
        with destination.open("wb") as out_file:
            out_file.write(upload.file.read())
        stored_paths.append(str(destination))
    return stored_paths


def save_proof_files(assignment_id: int, files: list[UploadFile]) -> list[str]:
    return save_files("action-reports", assignment_id, files)


def save_incident_attachments(incident_id: int, files: list[UploadFile]) -> list[str]:
    return save_files("incident-attachments", incident_id, files)
