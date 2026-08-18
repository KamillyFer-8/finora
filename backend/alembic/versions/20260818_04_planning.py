"""Create budgets, goals and contributions."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_04"
down_revision: str | Sequence[str] | None = "20260818_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "budgets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "category_id",
            sa.Uuid(),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("limit_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "category_id", "period_start", "period_end"),
    )
    op.create_index("ix_budgets_user_id", "budgets", ["user_id"])
    op.create_index("ix_budgets_category_id", "budgets", ["category_id"])
    op.create_table(
        "goals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("target_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("current_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("deadline", sa.Date()),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_goals_user_id", "goals", ["user_id"])
    op.create_table(
        "goal_contributions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "goal_id", sa.Uuid(), sa.ForeignKey("goals.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "account_id",
            sa.Uuid(),
            sa.ForeignKey("accounts.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("contributed_at", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    for column in ("user_id", "goal_id", "account_id"):
        op.create_index(f"ix_goal_contributions_{column}", "goal_contributions", [column])


def downgrade() -> None:
    op.drop_table("goal_contributions")
    op.drop_table("goals")
    op.drop_table("budgets")
