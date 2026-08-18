import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Card(Base):
    __tablename__ = "cards"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    last_four: Mapped[str] = mapped_column(String(4))
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    closing_day: Mapped[int] = mapped_column(Integer)
    due_day: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String(7), default="#B7FF2A")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="card", cascade="all, delete-orphan"
    )


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("card_id", "reference_month"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"), index=True
    )
    reference_month: Mapped[date] = mapped_column(Date)
    closing_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(10), default="open")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    card: Mapped[Card] = relationship(back_populates="invoices")
    installments: Mapped[list["CardInstallment"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )


class CardPurchase(Base):
    __tablename__ = "card_purchases"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(String(160))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    installment_count: Mapped[int] = mapped_column(Integer)
    purchase_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    installments: Mapped[list["CardInstallment"]] = relationship(
        back_populates="purchase", cascade="all, delete-orphan"
    )


class CardInstallment(Base):
    __tablename__ = "card_installments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    purchase_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("card_purchases.id", ondelete="CASCADE"), index=True
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    number: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    purchase: Mapped[CardPurchase] = relationship(back_populates="installments")
    invoice: Mapped[Invoice] = relationship(back_populates="installments")
