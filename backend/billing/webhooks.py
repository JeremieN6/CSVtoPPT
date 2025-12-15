"""Stripe webhook ingestion for billing events."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from auth.service import get_session

from . import service

logger = logging.getLogger(__name__)

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_WEBHOOK_SECRET:
    logger.warning("STRIPE_WEBHOOK_SECRET is not configured; webhook endpoint will reject requests.")

webhook_router = APIRouter(prefix="/billing", tags=["Billing Webhooks"])


@webhook_router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook non configuré.")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError as exc:
        logger.warning("Invalid payload for Stripe webhook: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload invalide.") from exc
    except stripe.error.SignatureVerificationError as exc:
        logger.warning("Invalid Stripe signature: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signature Stripe invalide.") from exc

    _dispatch_event(event, session)
    return {"received": True}


def _dispatch_event(event: stripe.Event, session: Session) -> None:
    event_type = event["type"]
    logger.info("Stripe event received: %s", event_type)

    handler_map = {
        "customer.subscription.created": _handle_subscription_change,
        "customer.subscription.updated": _handle_subscription_change,
        "invoice.payment_failed": _handle_invoice_failed,
        "invoice.payment_succeeded": _handle_invoice_succeeded,
        "customer.deleted": _handle_customer_deleted,
    }

    handler = handler_map.get(event_type)
    if handler:
        handler(event, session)
    else:
        logger.info("No handler for Stripe event %s", event_type)


def _handle_subscription_change(event: stripe.Event, session: Session) -> None:
    data = event["data"]["object"]
    customer_id = data.get("customer")
    status = data.get("status")
    user = service.find_user_by_customer_id(session, customer_id)
    if not user:
        logger.warning("Stripe customer %s not found locally for subscription event", customer_id)
        return

    service.sync_subscription_status(user, session, status)


def _handle_invoice_failed(event: stripe.Event, session: Session) -> None:
    data = event["data"]["object"]
    customer_id = data.get("customer")
    user = service.find_user_by_customer_id(session, customer_id)
    if not user:
        logger.warning("Stripe customer %s not found for invoice failure", customer_id)
        return
    service.sync_subscription_status(user, session, "unpaid")


def _handle_invoice_succeeded(event: stripe.Event, session: Session) -> None:
    data = event["data"]["object"]
    customer_id = data.get("customer")
    user = service.find_user_by_customer_id(session, customer_id)
    if not user:
        logger.warning("Stripe customer %s not found for invoice payment", customer_id)
        return
    service.sync_subscription_status(user, session, "active")


def _handle_customer_deleted(event: stripe.Event, session: Session) -> None:
    data = event["data"]["object"]
    customer_id = data.get("id")
    user = service.find_user_by_customer_id(session, customer_id)
    if not user:
        logger.warning("Deleted Stripe customer %s not found locally", customer_id)
        return
    service.mark_customer_as_deleted(user, session)
