import math
import uuid
from datetime import date

from fastapi import HTTPException, status

from app.models.planning import Budget, Goal, GoalContribution
from app.repositories.finance import FinanceRepository
from app.repositories.planning import PlanningRepository
from app.schemas.planning import (
    BudgetCreate,
    BudgetUpdate,
    ContributionCreate,
    GoalCreate,
    GoalUpdate,
)
from app.services.credit import add_months


class PlanningService:
    def __init__(
        self, repository: PlanningRepository, finance: FinanceRepository, user_id: uuid.UUID
    ) -> None:
        self.repository = repository
        self.finance = finance
        self.user_id = user_id

    def create_budget(self, data: BudgetCreate) -> Budget:
        category = self.finance.get_category(self.user_id, data.category_id)
        if not category or category.type != "expense":
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Categoria de despesa inválida"
            )
        if self.repository.find_budget(
            self.user_id, data.category_id, data.period_start, data.period_end
        ):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Já existe orçamento para a categoria e período"
            )
        budget = Budget(user_id=self.user_id, **data.model_dump())
        self.repository.add(budget)
        self.repository.commit()
        return budget

    def update_budget(self, budget_id: uuid.UUID, data: BudgetUpdate) -> Budget:
        budget = self._budget(budget_id)
        budget.limit_amount = data.limit_amount
        self.repository.commit()
        return budget

    def delete_budget(self, budget_id: uuid.UUID) -> None:
        self.repository.delete(self._budget(budget_id))
        self.repository.commit()

    def create_goal(self, data: GoalCreate) -> Goal:
        goal = Goal(user_id=self.user_id, **data.model_dump())
        self.repository.add(goal)
        self.repository.commit()
        return goal

    def update_goal(self, goal_id: uuid.UUID, data: GoalUpdate) -> Goal:
        goal = self._goal(goal_id)
        changes = data.model_dump(exclude_unset=True)
        if (target := changes.get("target_amount")) is not None and target < goal.current_amount:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Meta menor que o valor já acumulado"
            )
        for key, value in changes.items():
            setattr(goal, key, value)
        goal.status = "completed" if goal.current_amount >= goal.target_amount else "active"
        self.repository.commit()
        return goal

    def delete_goal(self, goal_id: uuid.UUID) -> None:
        goal = self._goal(goal_id)
        if goal.current_amount > 0:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Remova as contribuições antes de excluir a meta"
            )
        self.repository.delete(goal)
        self.repository.commit()

    def contribute(self, goal_id: uuid.UUID, data: ContributionCreate) -> GoalContribution:
        goal = self._goal(goal_id)
        account = self.finance.get_account(self.user_id, data.account_id)
        if not account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conta não encontrada")
        if data.amount > account.balance:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Saldo insuficiente")
        if data.amount > goal.target_amount - goal.current_amount:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Contribuição excede o valor restante"
            )
        contribution = GoalContribution(user_id=self.user_id, goal_id=goal.id, **data.model_dump())
        account.balance -= data.amount
        goal.current_amount += data.amount
        goal.status = "completed" if goal.current_amount >= goal.target_amount else "active"
        self.repository.add(contribution)
        self.repository.commit()
        return contribution

    def delete_contribution(self, contribution_id: uuid.UUID) -> None:
        contribution = self.repository.get_contribution(self.user_id, contribution_id)
        if not contribution:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Contribuição não encontrada")
        goal = self._goal(contribution.goal_id)
        account = self.finance.get_account(self.user_id, contribution.account_id)
        if not account:
            raise HTTPException(status.HTTP_409_CONFLICT, "Conta da contribuição indisponível")
        account.balance += contribution.amount
        goal.current_amount -= contribution.amount
        goal.status = "active"
        self.repository.delete(contribution)
        self.repository.commit()

    @staticmethod
    def forecast(goal: Goal) -> date | None:
        if not goal.contributions or goal.current_amount <= 0 or goal.status == "completed":
            return date.today() if goal.status == "completed" else None
        first = min(item.contributed_at for item in goal.contributions)
        months_elapsed = max(1, math.ceil((date.today() - first).days / 30))
        monthly_rate = goal.current_amount / months_elapsed
        months_remaining = math.ceil((goal.target_amount - goal.current_amount) / monthly_rate)
        return add_months(date.today(), months_remaining)

    def _budget(self, budget_id: uuid.UUID) -> Budget:
        budget = self.repository.get_budget(self.user_id, budget_id)
        if not budget:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Orçamento não encontrado")
        return budget

    def _goal(self, goal_id: uuid.UUID) -> Goal:
        goal = self.repository.get_goal(self.user_id, goal_id)
        if not goal:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Meta não encontrada")
        return goal
