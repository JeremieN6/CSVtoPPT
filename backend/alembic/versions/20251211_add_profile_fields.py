"""Add optional profile fields to users table."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "20251211_add_profile_fields"
down_revision = "20251210_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(length=150), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=150), nullable=True))
    op.add_column("users", sa.Column("address", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("company", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "company")
    op.drop_column("users", "phone")
    op.drop_column("users", "address")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
