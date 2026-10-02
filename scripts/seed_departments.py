from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.db.init_db import seed_departments  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def main():
    db = SessionLocal()
    try:
        seed_departments(db)
        print("Departments seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
