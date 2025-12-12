"""Add usage tracking fields to users."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20251212_add_usage_tracking"
down_revision = "20251211_add_profile_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("conversions_this_month", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("conversions_last_month", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("last_reset_date", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "last_reset_date")
    op.drop_column("users", "conversions_last_month")
    op.drop_column("users", "conversions_this_month")
