import datetime as dt
import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AccountType = Literal["checking", "savings", "wallet", "digital", "cash", "investment"]
TransactionType = Literal["income", "expense"]
TransactionStatus = Literal["pending", "completed", "cancelled"]


class AccountCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    institution: str = Field(min_length=2, max_length=100)
    type: AccountType
    balance: Decimal = Field(default=Decimal("0"), max_digits=14, decimal_places=2)


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    institution: str | None = Field(default=None, min_length=2, max_length=100)
    type: AccountType | None = None


class AccountResponse(AccountCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    currency: str
    is_active: bool
    created_at: dt.datetime


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    type: TransactionType
    color: str = Field(default="#B7FF2A", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str = Field(default="wallet", max_length=40)


class CategoryResponse(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class TransactionCreate(BaseModel):
    description: str = Field(min_length=2, max_length=160)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    type: TransactionType
    account_id: uuid.UUID
    category_id: uuid.UUID | None = None
    date: dt.date
    status: TransactionStatus = "completed"
    notes: str | None = Field(default=None, max_length=2000)


class TransactionUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=2, max_length=160)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    type: TransactionType | None = None
    account_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    date: dt.date | None = None
    status: TransactionStatus | None = None
    notes: str | None = Field(default=None, max_length=2000)


class TransactionResponse(TransactionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: dt.datetime


class TransactionPage(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int


class RecurrenceCreate(BaseModel):
    description: str = Field(min_length=2, max_length=160)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    type: TransactionType
    account_id: uuid.UUID
    category_id: uuid.UUID | None = None
    frequency: Literal["weekly", "monthly", "yearly"] = "monthly"
    interval: int = Field(default=1, ge=1, le=24)
    next_run_at: dt.date
    end_date: dt.date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class RecurrenceResponse(RecurrenceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_active: bool
    created_at: dt.datetime
