"""Add stripe customer id to users table."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251213_add_stripe_customer_id"
down_revision = "20251212_add_usage_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("stripe_customer_id", sa.String(length=255), nullable=True))
    op.create_unique_constraint(
        "uq_users_stripe_customer_id",
        "users",
        ["stripe_customer_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_users_stripe_customer_id", "users", type_="unique")
    op.drop_column("users", "stripe_customer_id")
