from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActionReport(Base):
    __tablename__ = "action_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("incident_assignments.id"), unique=True, index=True)
    officer_name: Mapped[str] = mapped_column(Text, default="")
    team_members: Mapped[str] = mapped_column(Text, default="")  # comma-separated names
    resources_used: Mapped[str] = mapped_column(Text, default="")
    arrival_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completion_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    action_taken: Mapped[str] = mapped_column(Text, default="")
    remarks: Mapped[str] = mapped_column(Text, default="")
    proof_file_paths: Mapped[str] = mapped_column(Text, default="[]")  # JSON-encoded list of stored file paths
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assignment = relationship("IncidentAssignment", back_populates="action_report")
