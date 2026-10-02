from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import UserRead
from app.services.auth_service import login_user, register_citizen

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Public citizen signup. Anyone can create a citizen account to report incidents."""
    return register_citizen(db, payload.full_name, payload.email, payload.password)


@router.post("/token", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, payload.email, payload.password)
    return {"access_token": result["access_token"], "token_type": result["token_type"]}


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return current_user
