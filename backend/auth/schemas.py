"""Pydantic schemas for authentication endpoints !"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserLogin(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserRead(UserBase):
    id: UUID
    plan: str = "free"
    credits: int = 10
    is_active: bool = True
    created_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    conversions_this_month: int = 0
    conversions_last_month: int = 0
    last_reset_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(Token):
    user: UserRead


class TokenPayload(BaseModel):
    sub: UUID
    email: EmailStr
    exp: int


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=150)
    last_name: Optional[str] = Field(default=None, max_length=150)
    address: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    company: Optional[str] = Field(default=None, max_length=255)

    model_config = ConfigDict(extra="forbid")
