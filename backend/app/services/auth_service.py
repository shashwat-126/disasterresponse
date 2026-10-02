from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def login_user(db: Session, email: str, password: str) -> dict:
    user = authenticate_user(db, email, password)
    token = create_access_token(subject=user.email, extra_claims={"role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


def register_citizen(db: Session, full_name: str, email: str, password: str) -> User:
    """Self-service signup, always creates a CITIZEN account. Department/admin accounts
    stay provisioned out-of-band so only vetted staff get scoped to a department."""
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An account with this email already exists")

    user = User(
        full_name=full_name,
        email=email,
        hashed_password=get_password_hash(password),
        role="CITIZEN",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
