import datetime as dt
import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BudgetCreate(BaseModel):
    category_id: uuid.UUID
    period_start: dt.date
    period_end: dt.date
    limit_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)

    @model_validator(mode="after")
    def valid_period(self) -> "BudgetCreate":
        if self.period_end < self.period_start:
            raise ValueError("O fim do período deve ser posterior ao início")
        return self


class BudgetUpdate(BaseModel):
    limit_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class BudgetResponse(BudgetCreate):
    id: uuid.UUID
    category_name: str
    category_color: str
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage: float
    alert_level: Literal["normal", "warning", "exceeded"]


class GoalCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    target_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    deadline: dt.date | None = None


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    target_amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    deadline: dt.date | None = None


class ContributionCreate(BaseModel):
    account_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    contributed_at: dt.date


class ContributionResponse(ContributionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    goal_id: uuid.UUID


class GoalResponse(GoalCreate):
    id: uuid.UUID
    current_amount: Decimal
    remaining_amount: Decimal
    percentage: float
    status: Literal["active", "completed"]
    forecast_date: dt.date | None
    contributions: list[ContributionResponse] = Field(default_factory=list)


class AlertResponse(BaseModel):
    id: str
    level: Literal["warning", "danger"]
    message: str
    budget_id: uuid.UUID
