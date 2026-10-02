from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IncidentAssignment(Base):
    __tablename__ = "incident_assignments"
    __table_args__ = (UniqueConstraint("incident_id", "department_id", name="uq_incident_department"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="ASSIGNED", index=True)
    is_lead: Mapped[bool] = mapped_column(default=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    action_report = relationship(
        "ActionReport", back_populates="assignment", uselist=False, cascade="all, delete-orphan"
    )
