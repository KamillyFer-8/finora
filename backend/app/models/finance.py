import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    institution: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20))
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(80))
    type: Mapped[str] = mapped_column(String(10))
    color: Mapped[str] = mapped_column(String(7), default="#B7FF2A")
    icon: Mapped[str] = mapped_column(String(40), default="wallet")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), index=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), index=True
    )
    description: Mapped[str] = mapped_column(String(160))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    type: Mapped[str] = mapped_column(String(10))
    date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(12), default="completed")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    account: Mapped[Account] = relationship(back_populates="transactions")
    category: Mapped[Category | None] = relationship()


class Recurrence(Base):
    __tablename__ = "recurrences"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL")
    )
    description: Mapped[str] = mapped_column(String(160))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    type: Mapped[str] = mapped_column(String(10))
    frequency: Mapped[str] = mapped_column(String(10))
    interval: Mapped[int] = mapped_column(Integer, default=1)
    next_run_at: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
