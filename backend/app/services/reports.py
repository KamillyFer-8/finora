import uuid
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from app.models.finance import Transaction
from app.models.planning import Budget
from app.repositories.planning import PlanningRepository
from app.repositories.reports import ReportsRepository
from app.schemas.reports import (
    AccountSnapshot,
    BudgetSnapshot,
    CardSnapshot,
    CashFlowPoint,
    CategorySlice,
    DashboardReport,
    GoalSnapshot,
    Metric,
    RecentTransaction,
)


def change(current: Decimal, previous: Decimal) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(float((current - previous) / abs(previous) * 100), 2)


class ReportsService:
    def __init__(
        self, repository: ReportsRepository, planning: PlanningRepository, user_id: uuid.UUID
    ) -> None:
        self.repository = repository
        self.planning = planning
        self.user_id = user_id

    def dashboard(self, start: date, end: date) -> DashboardReport:
        days = (end - start).days + 1
        previous_end = start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=days - 1)
        transactions = self.repository.transactions(self.user_id, start, end)
        previous = self.repository.transactions(self.user_id, previous_start, previous_end)
        income = sum((item.amount for item in transactions if item.type == "income"), Decimal("0"))
        expenses = sum(
            (item.amount for item in transactions if item.type == "expense"), Decimal("0")
        )
        previous_income = sum(
            (item.amount for item in previous if item.type == "income"), Decimal("0")
        )
        previous_expenses = sum(
            (item.amount for item in previous if item.type == "expense"), Decimal("0")
        )
        savings, previous_savings = income - expenses, previous_income - previous_expenses
        accounts = self.repository.accounts(self.user_id)
        cards = self.repository.cards(self.user_id)
        invoices = self.repository.invoices(self.user_id)
        goals = self.repository.goals(self.user_id)
        total_balance = (
            sum((item.balance for item in accounts), Decimal("0"))
            + sum((item.current_amount for item in goals), Decimal("0"))
            - sum((item.total for item in invoices), Decimal("0"))
        )
        cash_flow = self._cash_flow(transactions, start, end)
        categories = self._categories(transactions)
        budgets = self.repository.budgets(self.user_id, start, end)
        budget_items = [self._budget(item) for item in budgets]
        total_budget = sum((item.limit for item in budget_items), Decimal("0"))
        total_spent = sum((item.spent for item in budget_items), Decimal("0"))
        budget_percentage = (
            round(float(total_spent / total_budget * 100), 2) if total_budget else 0.0
        )
        alerts = [
            f"{item.name}: {item.percentage:.0f}% do orçamento utilizado."
            for item in budget_items
            if item.percentage >= 80
        ]
        overdue = [item for item in invoices if item.due_date < date.today()]
        if overdue:
            alerts.append(f"Você possui {len(overdue)} fatura(s) vencida(s).")
        category_map = self.repository.categories(self.user_id)
        recent = [
            RecentTransaction(
                id=item.id,
                description=item.description,
                type=item.type,
                amount=item.amount,
                date=item.date,
                status=item.status,
                category=category_map[item.category_id].name
                if item.category_id in category_map
                else "Sem categoria",
            )
            for item in self.repository.recent_transactions(self.user_id)
        ]
        current_net = total_balance
        period_net = income - expenses
        running = current_net - period_net
        net_worth: list[CashFlowPoint] = []
        for point in cash_flow:
            running += point.income - point.expense
            net_worth.append(
                CashFlowPoint(
                    label=point.label,
                    date=point.date,
                    income=Decimal("0"),
                    expense=Decimal("0"),
                    balance=running,
                )
            )
        return DashboardReport(
            period_start=start,
            period_end=end,
            total_balance=Metric(
                value=total_balance, change_percentage=change(savings, previous_savings)
            ),
            income=Metric(value=income, change_percentage=change(income, previous_income)),
            expenses=Metric(value=expenses, change_percentage=change(expenses, previous_expenses)),
            savings=Metric(value=savings, change_percentage=change(savings, previous_savings)),
            savings_rate=round(float(savings / income * 100), 2) if income else 0.0,
            budget_percentage=budget_percentage,
            cash_flow=cash_flow,
            net_worth=net_worth,
            categories=categories,
            accounts=[
                AccountSnapshot(
                    id=item.id, name=item.name, institution=item.institution, balance=item.balance
                )
                for item in accounts
            ],
            cards=[
                CardSnapshot(
                    id=item.id,
                    name=item.name,
                    used=sum(
                        (invoice.total for invoice in invoices if invoice.card_id == item.id),
                        Decimal("0"),
                    ),
                    limit=item.credit_limit,
                )
                for item in cards
            ],
            goals=[
                GoalSnapshot(
                    id=item.id,
                    name=item.name,
                    current=item.current_amount,
                    target=item.target_amount,
                    percentage=round(float(item.current_amount / item.target_amount * 100), 2),
                )
                for item in goals
            ],
            budgets=budget_items,
            recent_transactions=recent,
            alerts=alerts,
        )

    def _cash_flow(
        self, transactions: list[Transaction], start: date, end: date
    ) -> list[CashFlowPoint]:
        grouped: dict[date, list[Transaction]] = defaultdict(list)
        for item in transactions:
            key = (
                item.date if (end - start).days <= 45 else date(item.date.year, item.date.month, 1)
            )
            grouped[key].append(item)
        points = []
        for key in sorted(grouped):
            income = sum(
                (item.amount for item in grouped[key] if item.type == "income"), Decimal("0")
            )
            expense = sum(
                (item.amount for item in grouped[key] if item.type == "expense"), Decimal("0")
            )
            points.append(
                CashFlowPoint(
                    label=key.strftime("%d/%m")
                    if (end - start).days <= 45
                    else key.strftime("%m/%Y"),
                    date=key,
                    income=income,
                    expense=expense,
                    balance=income - expense,
                )
            )
        return points

    def _categories(self, transactions: list[Transaction]) -> list[CategorySlice]:
        category_map = self.repository.categories(self.user_id)
        totals: dict[uuid.UUID | None, Decimal] = defaultdict(Decimal)
        for item in transactions:
            if item.type == "expense":
                totals[item.category_id] += item.amount
        total = sum(totals.values(), Decimal("0"))
        return [
            CategorySlice(
                category_id=key,
                name=category_map[key].name if key in category_map else "Sem categoria",
                color=category_map[key].color if key in category_map else "#9BA1AA",
                amount=amount,
                percentage=round(float(amount / total * 100), 2) if total else 0.0,
            )
            for key, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)
        ]

    def _budget(self, budget: Budget) -> BudgetSnapshot:
        category = self.repository.categories(self.user_id).get(budget.category_id)
        spent = self.planning.spent(budget)
        return BudgetSnapshot(
            id=budget.id,
            name=category.name if category else "Categoria",
            spent=spent,
            limit=budget.limit_amount,
            percentage=round(float(spent / budget.limit_amount * 100), 2),
        )
