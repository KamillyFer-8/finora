"""recurrences

Revision ID: 20260818_06
Revises: 20260818_05
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260818_06"
down_revision: str | None = "20260818_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recurrences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("description", sa.String(160), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("frequency", sa.String(10), nullable=False),
        sa.Column("interval", sa.Integer(), nullable=False),
        sa.Column("next_run_at", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recurrences_user_id", "recurrences", ["user_id"])
    op.create_index("ix_recurrences_account_id", "recurrences", ["account_id"])
    op.create_index("ix_recurrences_next_run_at", "recurrences", ["next_run_at"])


def downgrade() -> None:
    op.drop_table("recurrences")
