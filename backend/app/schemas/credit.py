import datetime as dt
import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CardCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    last_four: str = Field(pattern=r"^\d{4}$")
    credit_limit: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    closing_day: int = Field(ge=1, le=28)
    due_day: int = Field(ge=1, le=28)
    color: str = Field(default="#B7FF2A", pattern=r"^#[0-9A-Fa-f]{6}$")


class CardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    credit_limit: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    closing_day: int | None = Field(default=None, ge=1, le=28)
    due_day: int | None = Field(default=None, ge=1, le=28)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CardResponse(CardCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    used_limit: Decimal
    available_limit: Decimal
    current_invoice: Decimal


class PurchaseCreate(BaseModel):
    description: str = Field(min_length=2, max_length=160)
    total_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    installment_count: int = Field(ge=1, le=48)
    purchase_date: dt.date


class PurchaseResponse(PurchaseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    card_id: uuid.UUID


class InstallmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    purchase_id: uuid.UUID
    number: int
    amount: Decimal
    description: str
    installment_count: int


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    card_id: uuid.UUID
    card_name: str
    reference_month: dt.date
    closing_date: dt.date
    due_date: dt.date
    total: Decimal
    status: Literal["open", "closed", "paid", "overdue"]
    installments: list[InstallmentResponse] = Field(default_factory=list)


class InvoicePayment(BaseModel):
    account_id: uuid.UUID
