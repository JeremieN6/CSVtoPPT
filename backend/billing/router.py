"""FastAPI router exposing authenticated billing endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.models import User
from auth.security import require_active_user
from auth.service import get_session

from . import service
from .service import BillingError

router = APIRouter(prefix="/billing", tags=["Billing"])


class CheckoutRequest(BaseModel):
    plan: str = Field("pro", pattern="^(?i)pro$")


class CheckoutResponse(BaseModel):
    url: str


class BillingStatusResponse(BaseModel):
    plan: str
    stripe_customer_id: Optional[str]
    conversions_this_month: int
    last_reset_date: Optional[str]


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(
    payload: CheckoutRequest,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
) -> CheckoutResponse:
    plan = payload.plan.lower()
    if plan != "pro":
        raise HTTPException(status_code=400, detail="Seul le plan Pro est disponible.")

    try:
        url = service.create_checkout_session(current_user, session)
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return CheckoutResponse(url=url)


@router.get("/portal", response_model=CheckoutResponse)
def open_billing_portal(
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
) -> CheckoutResponse:
    try:
        url = service.create_portal_session(current_user, session)
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return CheckoutResponse(url=url)


@router.get("/status", response_model=BillingStatusResponse)
def billing_status(current_user: User = Depends(require_active_user)) -> BillingStatusResponse:
    return BillingStatusResponse(
        plan=current_user.plan,
        stripe_customer_id=getattr(current_user, "stripe_customer_id", None),
        conversions_this_month=current_user.conversions_this_month,
        last_reset_date=current_user.last_reset_date.isoformat() if current_user.last_reset_date else None,
    )
