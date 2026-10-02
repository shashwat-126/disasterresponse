from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.user import User
from app.utils.enums import DepartmentCategory


def seed_admin_user(db: Session) -> None:
    settings = get_settings()
    user = db.query(User).filter(User.email == settings.admin_email).first()
    if user:
        return

    admin = User(
        full_name=settings.admin_full_name,
        email=settings.admin_email,
        hashed_password=get_password_hash(settings.admin_password),
        role="ADMIN",
        is_active=True,
    )
    db.add(admin)
    db.commit()


DEFAULT_DEPARTMENTS = [
    ("Fire & Rescue Services", "FIRE-01", DepartmentCategory.FIRE),
    ("Ambulance & Medical Services", "MED-01", DepartmentCategory.MEDICAL),
    ("City Police", "POLICE-01", DepartmentCategory.POLICE),
    ("Emergency Response Force", "ERF-01", DepartmentCategory.EMERGENCY_RESPONSE),
    ("Food & Relief Division", "RELIEF-01", DepartmentCategory.FOOD_RELIEF),
    ("Electricity Board", "ELEC-01", DepartmentCategory.ELECTRICITY),
    ("Water Supply Board", "WATER-01", DepartmentCategory.WATER_SUPPLY),
    ("Municipal Corporation", "MUNI-01", DepartmentCategory.MUNICIPAL),
    ("Disaster Management Authority", "DMA-01", DepartmentCategory.DISASTER_MANAGEMENT_AUTHORITY),
    ("NGO & Volunteer Network", "NGO-01", DepartmentCategory.NGO_VOLUNTEERS),
]


def seed_departments(db: Session) -> None:
    for name, code, category in DEFAULT_DEPARTMENTS:
        existing = db.query(Department).filter(Department.code == code).first()
        if existing:
            continue
        db.add(Department(name=name, code=code, category=category.value))
    db.commit()
