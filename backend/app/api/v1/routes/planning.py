import uuid
from decimal import Decimal

from fastapi import APIRouter, Response, status

from app.api.dependencies import CurrentUser, SessionDep
from app.models.planning import Budget, Goal
from app.repositories.finance import FinanceRepository
from app.repositories.planning import PlanningRepository
from app.schemas.planning import (
    AlertResponse,
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
    ContributionCreate,
    ContributionResponse,
    GoalCreate,
    GoalResponse,
    GoalUpdate,
)
from app.services.planning import PlanningService

budgets_router = APIRouter(prefix="/budgets", tags=["budgets"])
goals_router = APIRouter(prefix="/goals", tags=["goals"])
alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])


def service(session: SessionDep, user: CurrentUser) -> PlanningService:
    return PlanningService(PlanningRepository(session), FinanceRepository(session), user.id)


def budget_response(
    budget: Budget, planning: PlanningRepository, finance: FinanceRepository
) -> BudgetResponse:
    category = finance.get_category(budget.user_id, budget.category_id)
    if not category:
        raise RuntimeError("Budget category is missing")
    spent = planning.spent(budget)
    percentage = float(spent / budget.limit_amount * 100)
    level = "exceeded" if percentage >= 100 else "warning" if percentage >= 80 else "normal"
    return BudgetResponse(
        id=budget.id,
        category_id=budget.category_id,
        category_name=category.name,
        category_color=category.color,
        period_start=budget.period_start,
        period_end=budget.period_end,
        limit_amount=budget.limit_amount,
        spent_amount=spent,
        remaining_amount=budget.limit_amount - spent,
        percentage=round(percentage, 2),
        alert_level=level,
    )


def goal_response(goal: Goal) -> GoalResponse:
    percentage = float(goal.current_amount / goal.target_amount * Decimal("100"))
    return GoalResponse(
        id=goal.id,
        name=goal.name,
        target_amount=goal.target_amount,
        deadline=goal.deadline,
        current_amount=goal.current_amount,
        remaining_amount=goal.target_amount - goal.current_amount,
        percentage=round(percentage, 2),
        status=goal.status,
        forecast_date=PlanningService.forecast(goal),
        contributions=[ContributionResponse.model_validate(item) for item in goal.contributions],
    )


@budgets_router.get("", response_model=list[BudgetResponse])
def list_budgets(session: SessionDep, user: CurrentUser) -> list[BudgetResponse]:
    planning, finance = PlanningRepository(session), FinanceRepository(session)
    return [budget_response(item, planning, finance) for item in planning.list_budgets(user.id)]


@budgets_router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, session: SessionDep, user: CurrentUser) -> BudgetResponse:
    planning, finance = PlanningRepository(session), FinanceRepository(session)
    budget = PlanningService(planning, finance, user.id).create_budget(payload)
    return budget_response(budget, planning, finance)


@budgets_router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: uuid.UUID, payload: BudgetUpdate, session: SessionDep, user: CurrentUser
) -> BudgetResponse:
    planning, finance = PlanningRepository(session), FinanceRepository(session)
    budget = PlanningService(planning, finance, user.id).update_budget(budget_id, payload)
    return budget_response(budget, planning, finance)


@budgets_router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: uuid.UUID, session: SessionDep, user: CurrentUser) -> Response:
    service(session, user).delete_budget(budget_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@goals_router.get("", response_model=list[GoalResponse])
def list_goals(session: SessionDep, user: CurrentUser) -> list[GoalResponse]:
    return [goal_response(item) for item in PlanningRepository(session).list_goals(user.id)]


@goals_router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, session: SessionDep, user: CurrentUser) -> GoalResponse:
    return goal_response(service(session, user).create_goal(payload))


@goals_router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: uuid.UUID, payload: GoalUpdate, session: SessionDep, user: CurrentUser
) -> GoalResponse:
    return goal_response(service(session, user).update_goal(goal_id, payload))


@goals_router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: uuid.UUID, session: SessionDep, user: CurrentUser) -> Response:
    service(session, user).delete_goal(goal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@goals_router.post(
    "/{goal_id}/contributions",
    response_model=ContributionResponse,
    status_code=status.HTTP_201_CREATED,
)
def contribute(
    goal_id: uuid.UUID, payload: ContributionCreate, session: SessionDep, user: CurrentUser
) -> ContributionResponse:
    return ContributionResponse.model_validate(service(session, user).contribute(goal_id, payload))


@goals_router.delete("/contributions/{contribution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contribution(
    contribution_id: uuid.UUID, session: SessionDep, user: CurrentUser
) -> Response:
    service(session, user).delete_contribution(contribution_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@alerts_router.get("", response_model=list[AlertResponse])
def list_alerts(session: SessionDep, user: CurrentUser) -> list[AlertResponse]:
    planning, finance = PlanningRepository(session), FinanceRepository(session)
    alerts: list[AlertResponse] = []
    for budget in planning.list_budgets(user.id):
        item = budget_response(budget, planning, finance)
        if item.alert_level != "normal":
            level = "danger" if item.alert_level == "exceeded" else "warning"
            alerts.append(
                AlertResponse(
                    id=f"budget-{budget.id}",
                    level=level,
                    budget_id=budget.id,
                    message=f"{item.category_name}: {item.percentage:.0f}% do orçamento utilizado.",
                )
            )
    return alerts
