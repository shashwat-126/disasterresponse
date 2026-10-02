from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import (
    action_reports,
    allocations,
    analytics,
    assignments,
    attachments,
    audit,
    auth,
    damage_updates,
    dashboard,
    departments,
    exports,
    health,
    incidents,
    notifications,
    resource_requests,
)
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.init_db import seed_admin_user, seed_departments
from app.db.session import SessionLocal, engine
from app.models.action_report import ActionReport  # noqa: F401
from app.models.allocation import Allocation  # noqa: F401
from app.models.assignment import IncidentAssignment  # noqa: F401
from app.models.attachment import IncidentAttachment  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.damage_update import DamageUpdate  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.incident import Incident  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.resource_request import ResourceRequest  # noqa: F401
from app.models.user import User  # noqa: F401

settings = get_settings()
setup_logging()

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    with SessionLocal() as db:
        seed_admin_user(db)
        seed_departments(db)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(incidents.router, prefix=settings.api_prefix)
app.include_router(allocations.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(departments.router, prefix=settings.api_prefix)
app.include_router(assignments.router, prefix=settings.api_prefix)
app.include_router(attachments.router, prefix=settings.api_prefix)
app.include_router(notifications.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(audit.router, prefix=settings.api_prefix)
app.include_router(exports.router, prefix=settings.api_prefix)
app.include_router(resource_requests.router, prefix=settings.api_prefix)
app.include_router(damage_updates.router, prefix=settings.api_prefix)
app.include_router(action_reports.router, prefix=settings.api_prefix)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

Instrumentator().instrument(app).expose(app)
