import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.finance import Transaction
from app.models.planning import Budget, Goal, GoalContribution


class PlanningRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, model: object) -> None:
        self.session.add(model)

    def list_budgets(self, user_id: uuid.UUID) -> list[Budget]:
        return list(
            self.session.scalars(
                select(Budget).where(Budget.user_id == user_id).order_by(Budget.period_start.desc())
            )
        )

    def get_budget(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> Budget | None:
        return self.session.scalar(
            select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        )

    def find_budget(
        self, user_id: uuid.UUID, category_id: uuid.UUID, start: date, end: date
    ) -> Budget | None:
        return self.session.scalar(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.period_start == start,
                Budget.period_end == end,
            )
        )

    def spent(self, budget: Budget) -> Decimal:
        return self.session.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == budget.user_id,
                Transaction.category_id == budget.category_id,
                Transaction.type == "expense",
                Transaction.status == "completed",
                Transaction.date >= budget.period_start,
                Transaction.date <= budget.period_end,
            )
        ) or Decimal("0")

    def list_goals(self, user_id: uuid.UUID) -> list[Goal]:
        return list(
            self.session.scalars(
                select(Goal)
                .options(selectinload(Goal.contributions))
                .where(Goal.user_id == user_id)
                .order_by(Goal.created_at.desc())
            )
        )

    def get_goal(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal | None:
        return self.session.scalar(
            select(Goal)
            .options(selectinload(Goal.contributions))
            .where(Goal.id == goal_id, Goal.user_id == user_id)
        )

    def get_contribution(
        self, user_id: uuid.UUID, contribution_id: uuid.UUID
    ) -> GoalContribution | None:
        return self.session.scalar(
            select(GoalContribution).where(
                GoalContribution.id == contribution_id, GoalContribution.user_id == user_id
            )
        )

    def delete(self, model: object) -> None:
        self.session.delete(model)

    def commit(self) -> None:
        self.session.commit()
