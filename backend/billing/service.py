"""Business logic for Stripe billing flows."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import stripe
from sqlalchemy.orm import Session

from auth.models import User

logger = logging.getLogger(__name__)

# stripe.error module was removed in stripe>=10; fall back to the new location when needed.
try:
    from stripe.error import InvalidRequestError  # type: ignore
except ModuleNotFoundError:
    from stripe import InvalidRequestError  # type: ignore

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_PRO_ID = os.getenv("STRIPE_PRICE_PRO_ID")

# Frontend URLs (local fallback) so the same code works in prod and dev environnements.
FRONTEND_BASE_URL = (
    os.getenv("APP_BASE_URL")
    or os.getenv("APP_FRONTEND_URL")
    or os.getenv("FRONTEND_URL")
    or "http://localhost:5173"
).rstrip("/")
DASHBOARD_PATH = os.getenv("APP_DASHBOARD_PATH", "/mon-compte")
if not DASHBOARD_PATH.startswith("/"):
    DASHBOARD_PATH = f"/{DASHBOARD_PATH}"

DASHBOARD_URL = os.getenv("APP_DASHBOARD_URL", f"{FRONTEND_BASE_URL}{DASHBOARD_PATH}")
CHECKOUT_SUCCESS_URL = os.getenv(
    "STRIPE_CHECKOUT_SUCCESS_URL",
    f"{FRONTEND_BASE_URL}/convertisseur?checkout=success",
)
CHECKOUT_CANCEL_URL = os.getenv(
    "STRIPE_CHECKOUT_CANCEL_URL",
    f"{DASHBOARD_URL}?checkout=cancel",
)

if not STRIPE_SECRET_KEY:
    logger.warning("STRIPE_SECRET_KEY is not configured; billing endpoints will fail until set.")
else:
    stripe.api_key = STRIPE_SECRET_KEY


PRO_ACTIVE_STATUSES = {"trialing", "active", "past_due"}
PRO_INACTIVE_STATUSES = {"canceled", "unpaid", "incomplete_expired", "incomplete"}


class BillingError(Exception):
    """Raised when a billing operation fails."""


def ensure_stripe_customer(user: User, session: Session) -> str:
    """Return the Stripe customer id, creating one if necessary."""

    if user.stripe_customer_id:
        # Validate that the customer still exists in the current Stripe mode (test/prod)
        try:
            stripe.Customer.retrieve(user.stripe_customer_id)
            return user.stripe_customer_id
        except InvalidRequestError as exc:  # e.g., "No such customer" when env mismatch
            logger.warning("Stripe customer %s missing; recreating. %s", user.stripe_customer_id, exc)
            user.stripe_customer_id = None

    if not STRIPE_SECRET_KEY:
        raise BillingError("Stripe n'est pas configuré côté serveur.")

    logger.info("Creating Stripe customer for user %s", user.email)
    customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": str(user.id)},
    )
    user.stripe_customer_id = customer["id"]
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.stripe_customer_id


def create_checkout_session(user: User, session: Session) -> str:
    """Create a Stripe Checkout session for the Pro subscription."""

    if not STRIPE_PRICE_PRO_ID:
        raise BillingError("Le prix STRIPE_PRICE_PRO_ID n'est pas configuré.")

    customer_id = ensure_stripe_customer(user, session)

    checkout_session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        success_url=CHECKOUT_SUCCESS_URL,
        cancel_url=CHECKOUT_CANCEL_URL,
        line_items=[{"price": STRIPE_PRICE_PRO_ID, "quantity": 1}],
        allow_promotion_codes=True,
        metadata={"user_id": str(user.id)},
    )
    return checkout_session["url"]


def create_portal_session(user: User, session: Session) -> str:
    """Return a Stripe billing-portal URL for the given user."""

    customer_id = ensure_stripe_customer(user, session)
    portal_session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=DASHBOARD_URL,
    )
    return portal_session["url"]


def sync_subscription_status(user: User, session: Session, status: Optional[str]) -> bool:
    """Synchronize the local user plan with the Stripe subscription status."""

    normalized = (status or "").lower()
    previous_plan = (user.plan or "free").lower()

    if normalized in PRO_ACTIVE_STATUSES:
        if previous_plan == "pro":
            return False
        _apply_pro_plan(user)
        session.add(user)
        session.commit()
        logger.info("User %s upgraded to Pro via webhook.", user.email)
        return True

    if normalized in PRO_INACTIVE_STATUSES:
        if previous_plan == "free":
            return False
        _apply_free_plan(user)
        session.add(user)
        session.commit()
        logger.info("User %s downgraded to Free via webhook.", user.email)
        return True

    logger.info("Subscription status %s ignored for user %s.", normalized, user.email)
    return False


def mark_customer_as_deleted(user: User, session: Session) -> bool:
    """Downgrade the user if Stripe deletes the customer."""

    if (user.plan or "free").lower() == "free" and not user.stripe_customer_id:
        return False
    _apply_free_plan(user)
    user.stripe_customer_id = None
    session.add(user)
    session.commit()
    logger.info("Customer %s deleted on Stripe; user downgraded.", user.email)
    return True


def _apply_pro_plan(user: User) -> None:
    now = datetime.now(timezone.utc)
    user.plan = "pro"
    user.conversions_this_month = 0
    user.last_reset_date = now


def _apply_free_plan(user: User) -> None:
    user.plan = "free"
    # We keep existing counters so Module J can continue enforcing Free limits naturally.


def find_user_by_customer_id(session: Session, customer_id: Optional[str]) -> Optional[User]:
    """Return the user associated with a Stripe customer id."""

    if not customer_id:
        return None
    return session.query(User).filter(User.stripe_customer_id == customer_id).one_or_none()
