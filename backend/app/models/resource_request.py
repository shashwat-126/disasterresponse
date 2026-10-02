from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ResourceRequest(Base):
    """A department's request for extra resources on an incident, raised from the ground
    (e.g. after filing an action report or damage update and realizing the initial
    allocation is insufficient). Admin reviews and approves/rejects/fulfills it.
    """

    __tablename__ = "resource_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    resource_type: Mapped[str] = mapped_column(String(50))  # ambulances | rescue_teams | vehicles | food_kits | water_liters | shelters | other
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    justification: Mapped[str] = mapped_column(Text, default="")

    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolution_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="resource_requests")
    department = relationship("Department")
