"""FastAPI router exposing auth endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import schemas
from auth.models import User
from auth.security import require_active_user
from auth.service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_session,
    get_user_by_email,
)

router = APIRouter(tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    payload: schemas.UserCreate,
    session: Session = Depends(get_session),
) -> dict:
    existing = get_user_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Un compte utilise déjà cet email.")
    create_user(session, payload)
    return {"success": True}


@router.post("/login", response_model=schemas.LoginResponse)
def login_user(
    payload: schemas.UserLogin,
    session: Session = Depends(get_session),
):
    user = authenticate_user(session, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide.")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return schemas.LoginResponse(
        access_token=token,
        token_type="bearer",
        user=schemas.UserRead.model_validate(user, from_attributes=True),
    )


@router.get("/me", response_model=schemas.UserRead)
def read_current_user(current_user: User = Depends(require_active_user)) -> schemas.UserRead:
    return schemas.UserRead.model_validate(current_user, from_attributes=True)
