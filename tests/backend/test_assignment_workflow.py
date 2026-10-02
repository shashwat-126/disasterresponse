from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.init_db import seed_departments  # noqa: E402
from app.models.action_report import ActionReport  # noqa: E402
from app.models.allocation import Allocation  # noqa: E402
from app.models.assignment import IncidentAssignment  # noqa: E402
from app.models.department import Department  # noqa: E402
from app.models.incident import Incident  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.assignment_service import (  # noqa: E402
    all_assignments_completed,
    auto_assign_departments,
    complete_assignment,
)


def _make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _make_incident(db, disaster_type="flood", severity="HIGH"):
    user = User(full_name="Reporter", email=f"r-{disaster_type}@test.local", hashed_password="x", role="CITIZEN")
    db.add(user)
    db.commit()
    incident = Incident(
        title="Test incident",
        description="Test description",
        disaster_type=disaster_type,
        location="Test City",
        people_affected=100,
        injuries=5,
        severity=severity,
        created_by=user.id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def test_flood_auto_assigns_expected_departments():
    db = _make_session()
    seed_departments(db)
    incident = _make_incident(db, disaster_type="flood", severity="HIGH")

    assignments = auto_assign_departments(db, incident)
    department_categories = {a.department.category for a in assignments}

    assert "EMERGENCY_RESPONSE" in department_categories
    assert "MEDICAL" in department_categories
    assert "FOOD_RELIEF" in department_categories
    # Disaster management authority always coordinates.
    assert "DISASTER_MANAGEMENT_AUTHORITY" in department_categories
    # HIGH severity escalates police + NGO involvement.
    assert "POLICE" in department_categories
    assert "NGO_VOLUNTEERS" in department_categories


def test_auto_assign_is_idempotent():
    db = _make_session()
    seed_departments(db)
    incident = _make_incident(db)

    first_pass = auto_assign_departments(db, incident)
    db.refresh(incident)
    second_pass = auto_assign_departments(db, incident)

    assert len(first_pass) > 0
    assert len(second_pass) == 0  # nothing new created on the second call


def test_incident_not_resolvable_until_all_departments_complete():
    db = _make_session()
    seed_departments(db)
    incident = _make_incident(db)
    auto_assign_departments(db, incident)
    db.refresh(incident)

    assert all_assignments_completed(incident) is False

    for assignment in incident.assignments:
        complete_assignment(db, assignment)

    db.refresh(incident)
    assert all_assignments_completed(incident) is True
