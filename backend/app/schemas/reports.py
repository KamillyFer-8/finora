import datetime as dt
import uuid
from decimal import Decimal

from pydantic import BaseModel


class Metric(BaseModel):
    value: Decimal
    change_percentage: float


class CashFlowPoint(BaseModel):
    label: str
    date: dt.date
    income: Decimal
    expense: Decimal
    balance: Decimal


class CategorySlice(BaseModel):
    category_id: uuid.UUID | None
    name: str
    color: str
    amount: Decimal
    percentage: float


class AccountSnapshot(BaseModel):
    id: uuid.UUID
    name: str
    institution: str
    balance: Decimal


class CardSnapshot(BaseModel):
    id: uuid.UUID
    name: str
    used: Decimal
    limit: Decimal


class GoalSnapshot(BaseModel):
    id: uuid.UUID
    name: str
    current: Decimal
    target: Decimal
    percentage: float


class BudgetSnapshot(BaseModel):
    id: uuid.UUID
    name: str
    spent: Decimal
    limit: Decimal
    percentage: float


class RecentTransaction(BaseModel):
    id: uuid.UUID
    description: str
    type: str
    amount: Decimal
    date: dt.date
    status: str
    category: str


class DashboardReport(BaseModel):
    period_start: dt.date
    period_end: dt.date
    total_balance: Metric
    income: Metric
    expenses: Metric
    savings: Metric
    savings_rate: float
    budget_percentage: float
    cash_flow: list[CashFlowPoint]
    net_worth: list[CashFlowPoint]
    categories: list[CategorySlice]
    accounts: list[AccountSnapshot]
    cards: list[CardSnapshot]
    goals: list[GoalSnapshot]
    budgets: list[BudgetSnapshot]
    recent_transactions: list[RecentTransaction]
    alerts: list[str]
