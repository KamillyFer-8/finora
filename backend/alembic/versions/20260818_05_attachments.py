"""Create attachments."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_05"
down_revision: str | Sequence[str] | None = "20260818_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "transaction_id", sa.Uuid(), sa.ForeignKey("transactions.id", ondelete="CASCADE")
        ),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False, unique=True),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_attachments_user_id", "attachments", ["user_id"])
    op.create_index("ix_attachments_transaction_id", "attachments", ["transaction_id"])


def downgrade() -> None:
    op.drop_table("attachments")
