"""Business services for authentication and persistence."""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import bcrypt
from dotenv import load_dotenv
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from auth.models import User
from auth.schemas import UserCreate

BASE_DIR = Path(__file__).resolve().parents[2]


def _load_env() -> None:
    """Load env with production priority; do not override already-set values."""

    for env_name in (".env.production", ".env.local", ".env"):
        env_path = BASE_DIR / env_name
        if env_path.exists():
            load_dotenv(env_path, override=False)
            break


_load_env()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL n'est pas défini. Ajoute ta chaîne Supabase/PostgreSQL dans .env.local"
    )

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def get_session() -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session for FastAPI dependencies."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return (
        session.query(User)
        .filter(User.email == _normalize_email(email))
        .one_or_none()
    )


def create_user(session: Session, user_in: UserCreate) -> User:
    hashed = hash_password(user_in.password)
    db_user = User(
        email=_normalize_email(user_in.email),
        password_hash=hashed,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
