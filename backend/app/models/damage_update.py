from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DamageUpdate(Base):
    """An on-ground damage assessment update. Any department currently assigned to the
    incident (not just the reporting citizen) can add one as they discover more about the
    real situation on-site — e.g. more people affected than first reported, a building
    collapse found while responding to a flood, etc. Every other assigned department and
    the admin are notified so the picture everyone is working from stays current.
    """

    __tablename__ = "damage_updates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    reported_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    description: Mapped[str] = mapped_column(Text)
    revised_people_affected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    revised_injuries: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity_reassessment: Mapped[str | None] = mapped_column(Text, nullable=True)  # e.g. "worse than initial AI estimate"

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="damage_updates")
    department = relationship("Department")
