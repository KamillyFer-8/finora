import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.credit import Card, Invoice
from app.models.finance import Account, Category, Transaction
from app.models.planning import Budget, Goal


class ReportsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def transactions(self, user_id: uuid.UUID, start: date, end: date) -> list[Transaction]:
        return list(
            self.session.scalars(
                select(Transaction)
                .where(
                    Transaction.user_id == user_id,
                    Transaction.status == "completed",
                    Transaction.date >= start,
                    Transaction.date <= end,
                )
                .order_by(Transaction.date)
            )
        )

    def recent_transactions(self, user_id: uuid.UUID, limit: int = 6) -> list[Transaction]:
        return list(
            self.session.scalars(
                select(Transaction)
                .where(Transaction.user_id == user_id)
                .order_by(Transaction.date.desc(), Transaction.created_at.desc())
                .limit(limit)
            )
        )

    def accounts(self, user_id: uuid.UUID) -> list[Account]:
        return list(
            self.session.scalars(
                select(Account)
                .where(Account.user_id == user_id, Account.is_active.is_(True))
                .order_by(Account.balance.desc())
            )
        )

    def categories(self, user_id: uuid.UUID) -> dict[uuid.UUID, Category]:
        items = self.session.scalars(select(Category).where(Category.user_id == user_id))
        return {item.id: item for item in items}

    def cards(self, user_id: uuid.UUID) -> list[Card]:
        return list(
            self.session.scalars(
                select(Card).where(Card.user_id == user_id, Card.is_active.is_(True))
            )
        )

    def invoices(self, user_id: uuid.UUID) -> list[Invoice]:
        return list(
            self.session.scalars(
                select(Invoice).where(Invoice.user_id == user_id, Invoice.status != "paid")
            )
        )

    def goals(self, user_id: uuid.UUID) -> list[Goal]:
        return list(
            self.session.scalars(
                select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())
            )
        )

    def budgets(self, user_id: uuid.UUID, start: date, end: date) -> list[Budget]:
        return list(
            self.session.scalars(
                select(Budget).where(
                    Budget.user_id == user_id,
                    Budget.period_start <= end,
                    Budget.period_end >= start,
                )
            )
        )
