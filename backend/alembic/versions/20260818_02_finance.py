"""Create accounts, categories and transactions."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_02"
down_revision: str | Sequence[str] | None = "20260818_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    def timestamps() -> list[sa.Column[object]]:
        return [
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        ]

    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("institution", sa.String(100), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("icon", sa.String(40), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])
    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "account_id",
            sa.Uuid(),
            sa.ForeignKey("accounts.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("category_id", sa.Uuid(), sa.ForeignKey("categories.id", ondelete="SET NULL")),
        sa.Column("description", sa.String(160), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("notes", sa.Text()),
        *timestamps(),
    )
    for column in ("user_id", "account_id", "category_id", "date"):
        op.create_index(f"ix_transactions_{column}", "transactions", [column])


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("accounts")
