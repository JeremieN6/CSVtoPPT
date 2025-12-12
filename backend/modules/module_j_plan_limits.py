"""Business rules for Free vs Pro plan enforcement (Module J).

This module is intentionally standalone so it can be imported both by the
FastAPI layer (Module F) and by the data pipeline (Modules A-E & H).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

FREE_MONTHLY_LIMIT = 10
FREE_MAX_SLIDES = 8
FREE_MAX_ROWS = 5_000
FREE_AI_STYLE = "light"
FREE_TEMPLATE = "default"
PRO_TEMPLATE = "pro_template"


@dataclass
class PlanParameters:
    """Parameters consumed by downstream modules."""

    max_slides: Optional[int]
    ai_style: str
    watermark: bool
    template: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_slides": self.max_slides,
            "ai_style": self.ai_style,
            "watermark": self.watermark,
            "template": self.template,
        }


def get_user_plan(user: Any) -> str:
    """Return the normalized plan name for a user."""

    plan = getattr(user, "plan", None) or "free"
    return plan.strip().lower()


def apply_plan_parameters(user: Any) -> PlanParameters:
    """Return downstream parameters derived from the user's plan."""

    plan = get_user_plan(user)
    if plan == "pro":
        return PlanParameters(
            max_slides=None,
            ai_style="executive",
            watermark=False,
            template=PRO_TEMPLATE,
        )

    # Default to Free plan safeguards
    return PlanParameters(
        max_slides=FREE_MAX_SLIDES,
        ai_style=FREE_AI_STYLE,
        watermark=True,
        template=FREE_TEMPLATE,
    )


def check_usage_limits(user: Any, dataframe: Any, requested_slide_count: Optional[int]) -> Dict[str, Any]:
    """Validate plan limits and return the enforcement payload."""

    plan = get_user_plan(user)
    params = apply_plan_parameters(user)

    _reset_monthly_quota_if_needed(user)

    if plan == "pro":
        return _allow_and_increment(user, params)

    # From this point we are within the Free tier ruleset.
    conversions_this_month = int(getattr(user, "conversions_this_month", 0) or 0)
    if conversions_this_month >= FREE_MONTHLY_LIMIT:
        return {
            "allowed": False,
            "error": "Vous avez atteint la limite de 10 conversions mensuelles du plan Free.",
            "params": None,
        }

    row_count = _extract_row_count(dataframe)
    if row_count > FREE_MAX_ROWS:
        return {
            "allowed": False,
            "error": "Votre fichier dépasse la limite du plan Free.",
            "params": None,
        }

    if requested_slide_count and requested_slide_count > FREE_MAX_SLIDES:
        return {
            "allowed": False,
            "error": "Le plan Free est limité à 8 slides par présentation.",
            "params": None,
        }

    return _allow_and_increment(user, params)


def _allow_and_increment(user: Any, params: PlanParameters) -> Dict[str, Any]:
    """Increment the usage counter (if present) and return the allow payload."""

    current_conversions = int(getattr(user, "conversions_this_month", 0) or 0)
    setattr(user, "conversions_this_month", current_conversions + 1)
    if not getattr(user, "last_reset_date", None):
        setattr(user, "last_reset_date", datetime.now(timezone.utc))

    return {
        "allowed": True,
        "error": None,
        "params": params.to_dict(),
    }


def _reset_monthly_quota_if_needed(user: Any) -> None:
    """Reset the monthly quota counter when a new month starts."""

    now = datetime.now(timezone.utc)
    last_reset = getattr(user, "last_reset_date", None)
    previous_value = int(getattr(user, "conversions_this_month", 0) or 0)

    if last_reset is not None and not isinstance(last_reset, datetime):
        last_reset = None

    if last_reset is not None and last_reset.tzinfo is None:
        last_reset = last_reset.replace(tzinfo=timezone.utc)

    if last_reset is None or last_reset.year != now.year or last_reset.month != now.month:
        setattr(user, "conversions_last_month", previous_value)
        setattr(user, "conversions_this_month", 0)
        setattr(user, "last_reset_date", now)


def _extract_row_count(dataframe: Any) -> int:
    """Try to infer the number of rows of an arbitrary tabular object."""

    if dataframe is None:
        return 0

    if hasattr(dataframe, "shape") and dataframe.shape:
        return int(dataframe.shape[0])

    try:
        return len(dataframe)
    except TypeError:
        return 0


# ==========================
# 🧪 TESTS UNITAIRES (simple)
# ==========================
if __name__ == "__main__":
    class DummyUser:
        def __init__(self, plan="free", conversions_this_month=0, last_reset_date=None):
            self.plan = plan
            self.conversions_this_month = conversions_this_month
            self.last_reset_date = last_reset_date

    class DummyDataFrame:
        def __init__(self, rows):
            self.shape = (rows, 5)

    # 1. Plan Free dataset trop gros
    free_user = DummyUser()
    response = check_usage_limits(free_user, DummyDataFrame(6000), requested_slide_count=4)
    assert response["allowed"] is False and "dépasse la limite" in response["error"]

    # 2. Plan Free avec trop de conversions
    free_user = DummyUser(conversions_this_month=10)
    response = check_usage_limits(free_user, DummyDataFrame(10), requested_slide_count=4)
    assert response["allowed"] is False and "limite" in response["error"]

    # 3. Plan Free avec graphiques non restreints (devrait passer)
    free_user = DummyUser()
    response = check_usage_limits(free_user, DummyDataFrame(100), requested_slide_count=4)
    assert response["allowed"] is True

    # 4. Plan Pro sans limitation
    pro_user = DummyUser(plan="pro")
    response = check_usage_limits(pro_user, DummyDataFrame(25_000), requested_slide_count=50)
    assert response["allowed"] is True and response["params"]["max_slides"] is None

    print("Tous les tests manuels du Module J sont passés ✔️")
