"""Create cards, invoices, purchases and installments."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_03"
down_revision: str | Sequence[str] | None = "20260818_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cards",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("last_four", sa.String(4), nullable=False),
        sa.Column("credit_limit", sa.Numeric(14, 2), nullable=False),
        sa.Column("closing_day", sa.Integer(), nullable=False),
        sa.Column("due_day", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cards_user_id", "cards", ["user_id"])
    op.create_table(
        "invoices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "card_id", sa.Uuid(), sa.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("reference_month", sa.Date(), nullable=False),
        sa.Column("closing_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("total", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("card_id", "reference_month"),
    )
    op.create_index("ix_invoices_user_id", "invoices", ["user_id"])
    op.create_index("ix_invoices_card_id", "invoices", ["card_id"])
    op.create_index("ix_invoices_due_date", "invoices", ["due_date"])
    op.create_table(
        "card_purchases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "card_id", sa.Uuid(), sa.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("description", sa.String(160), nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("installment_count", sa.Integer(), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_card_purchases_user_id", "card_purchases", ["user_id"])
    op.create_index("ix_card_purchases_card_id", "card_purchases", ["card_id"])
    op.create_table(
        "card_installments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "purchase_id",
            sa.Uuid(),
            sa.ForeignKey("card_purchases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "invoice_id",
            sa.Uuid(),
            sa.ForeignKey("invoices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
    )
    op.create_index("ix_card_installments_purchase_id", "card_installments", ["purchase_id"])
    op.create_index("ix_card_installments_invoice_id", "card_installments", ["invoice_id"])


def downgrade() -> None:
    op.drop_table("card_installments")
    op.drop_table("card_purchases")
    op.drop_table("invoices")
    op.drop_table("cards")
