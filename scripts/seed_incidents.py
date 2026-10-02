from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.db.session import SessionLocal  # noqa: E402
from app.models.incident import Incident  # noqa: E402
from app.models.user import User  # noqa: E402


def main():
    db = SessionLocal()
    try:
        admin = db.query(User).first()
        if not admin:
            raise RuntimeError("Seed a user first.")
        if db.query(Incident).count() > 0:
            print("Incidents already seeded.")
            return

        items = [
            Incident(
                title="Urban flood near ring road",
                description="Water level rising across low-lying streets.",
                disaster_type="flood",
                location="Bangalore Urban",
                people_affected=140,
                injuries=8,
                severity="HIGH",
                prediction_confidence=0.81,
                model_version="seed",
                created_by=admin.id,
            ),
            Incident(
                title="Minor landslide on hillside route",
                description="Road partially blocked after rainfall.",
                disaster_type="landslide",
                location="Coorg",
                people_affected=18,
                injuries=1,
                severity="MEDIUM",
                prediction_confidence=0.62,
                model_version="seed",
                created_by=admin.id,
            ),
        ]
        db.add_all(items)
        db.commit()
        print("Incidents seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
