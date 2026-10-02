from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.security import get_password_hash  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.department import Department  # noqa: E402
from app.models.user import User  # noqa: E402


def main():
    db = SessionLocal()
    try:
        departments = {d.code: d for d in db.query(Department).all()}

        # One dedicated login per department so each department can actually be
        # demoed/tested in isolation, not just Fire. Password pattern is deliberately
        # predictable for a local dev/demo seed — never do this for a real deployment.
        department_logins = [
            ("FIRE-01", "Fire Dept Staff", "fire1@eadrp.com"),
            ("MED-01", "Medical Dept Staff", "medical1@eadrp.com"),
            ("POLICE-01", "Police Dept Staff", "police1@eadrp.com"),
            ("ERF-01", "Emergency Response Staff", "erf1@eadrp.com"),
            ("RELIEF-01", "Food & Relief Staff", "relief1@eadrp.com"),
            ("ELEC-01", "Electricity Board Staff", "electricity1@eadrp.com"),
            ("WATER-01", "Water Supply Staff", "water1@eadrp.com"),
            ("MUNI-01", "Municipal Corp Staff", "municipal1@eadrp.com"),
            ("DMA-01", "Disaster Mgmt Authority Staff", "dma1@eadrp.com"),
            ("NGO-01", "NGO & Volunteer Staff", "ngo1@eadrp.com"),
        ]

        samples = [
            ("Coordinator One", "coord1@eadrp.com", "Coordinator@123", "ADMIN", None),
            ("Responder One", "resp1@eadrp.com", "Responder@123", "RESPONDER", None),
            ("Citizen One", "citizen1@eadrp.com", "Citizen@123", "CITIZEN", None),
        ]
        for code, full_name, email in department_logins:
            dept = departments.get(code)
            samples.append((full_name, email, f"{code.split('-')[0].title()}Staff@123", "DEPARTMENT_STAFF", dept.id if dept else None))

        for full_name, email, password, role, department_id in samples:
            exists = db.query(User).filter(User.email == email).first()
            if exists:
                continue
            db.add(
                User(
                    full_name=full_name,
                    email=email,
                    hashed_password=get_password_hash(password),
                    role=role,
                    department_id=department_id,
                )
            )
        db.commit()
        print("Users seeded — one login per department. Run seed_departments.py first if department_id ends up None.")
        for code, full_name, email in department_logins:
            print(f"  {code:10s} {email:28s} password: {code.split('-')[0].title()}Staff@123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
