"""Add downloads tracking columns to users table."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251214_add_downloads_tracking"
down_revision = "20251213_add_stripe_customer_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("downloads_this_month", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("downloads_last_month", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("users", "downloads_last_month")
    op.drop_column("users", "downloads_this_month")
