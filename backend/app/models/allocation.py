from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Allocation(Base):
    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    ambulances: Mapped[int] = mapped_column(Integer, default=0)
    rescue_teams: Mapped[int] = mapped_column(Integer, default=0)
    vehicles: Mapped[int] = mapped_column(Integer, default=0)
    food_kits: Mapped[int] = mapped_column(Integer, default=0)
    water_liters: Mapped[int] = mapped_column(Integer, default=0)
    shelters: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="allocations")
