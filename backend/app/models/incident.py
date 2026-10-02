from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)
    disaster_type: Mapped[str] = mapped_column(String(50), index=True)
    location: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    people_affected: Mapped[int] = mapped_column(Integer)
    injuries: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED")
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    prediction_confidence: Mapped[float] = mapped_column(default=0.0)
    model_version: Mapped[str] = mapped_column(String(50), default="fallback-v1")
    risk_score: Mapped[float] = mapped_column(default=0.0)
    priority_level: Mapped[str] = mapped_column(String(10), default="P3")
    estimated_response_minutes: Mapped[int] = mapped_column(Integer, default=90)
    secondary_hazards: Mapped[str] = mapped_column(Text, default="[]")
    immediate_recommendations: Mapped[str] = mapped_column(Text, default="[]")
    explanation_summary: Mapped[str] = mapped_column(Text, default="")
    top_signals: Mapped[str] = mapped_column(Text, default="[]")
    additional_info: Mapped[str] = mapped_column(Text, default="")
    possible_duplicate_of: Mapped[int | None] = mapped_column(ForeignKey("incidents.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    allocations = relationship("Allocation", back_populates="incident", cascade="all, delete-orphan")
    assignments = relationship("IncidentAssignment", back_populates="incident", cascade="all, delete-orphan")
    attachments = relationship("IncidentAttachment", back_populates="incident", cascade="all, delete-orphan")
    resource_requests = relationship(
        "ResourceRequest", back_populates="incident", cascade="all, delete-orphan"
    )
    damage_updates = relationship(
        "DamageUpdate", back_populates="incident", cascade="all, delete-orphan",
        order_by="DamageUpdate.created_at",
    )
