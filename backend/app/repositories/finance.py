import uuid
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.finance import Account, Category, Recurrence, Transaction


class FinanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_accounts(self, user_id: uuid.UUID) -> list[Account]:
        return list(
            self.session.scalars(
                select(Account)
                .where(Account.user_id == user_id, Account.is_active.is_(True))
                .order_by(Account.created_at)
            )
        )

    def get_account(self, user_id: uuid.UUID, account_id: uuid.UUID) -> Account | None:
        return self.session.scalar(
            select(Account).where(
                Account.id == account_id, Account.user_id == user_id, Account.is_active.is_(True)
            )
        )

    def add(self, model: object) -> None:
        self.session.add(model)

    def list_categories(self, user_id: uuid.UUID, type_: str | None = None) -> list[Category]:
        query = select(Category).where(Category.user_id == user_id)
        if type_:
            query = query.where(Category.type == type_)
        return list(self.session.scalars(query.order_by(Category.name)))

    def get_category(self, user_id: uuid.UUID, category_id: uuid.UUID) -> Category | None:
        return self.session.scalar(
            select(Category).where(Category.id == category_id, Category.user_id == user_id)
        )

    def get_transaction(self, user_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction | None:
        return self.session.scalar(
            select(Transaction).where(
                Transaction.id == transaction_id, Transaction.user_id == user_id
            )
        )

    def list_transactions(
        self,
        user_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
        search: str | None,
        type_: str | None,
        status: str | None,
        account_id: uuid.UUID | None,
        category_id: uuid.UUID | None,
        start_date: date | None,
        end_date: date | None,
        sort: str,
    ) -> tuple[list[Transaction], int]:
        filters = [Transaction.user_id == user_id]
        if search:
            filters.append(
                or_(
                    Transaction.description.ilike(f"%{search}%"),
                    Transaction.notes.ilike(f"%{search}%"),
                )
            )
        for value, column in (
            (type_, Transaction.type),
            (status, Transaction.status),
            (account_id, Transaction.account_id),
            (category_id, Transaction.category_id),
        ):
            if value is not None:
                filters.append(column == value)
        if start_date:
            filters.append(Transaction.date >= start_date)
        if end_date:
            filters.append(Transaction.date <= end_date)
        order = (
            Transaction.date.asc()
            if sort == "date_asc"
            else Transaction.amount.desc()
            if sort == "amount_desc"
            else Transaction.amount.asc()
            if sort == "amount_asc"
            else Transaction.date.desc()
        )
        total = (
            self.session.scalar(select(func.count()).select_from(Transaction).where(*filters)) or 0
        )
        items = list(
            self.session.scalars(
                select(Transaction)
                .where(*filters)
                .order_by(order, Transaction.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def delete(self, model: object) -> None:
        self.session.delete(model)

    def list_recurrences(self, user_id: uuid.UUID) -> list[Recurrence]:
        return list(
            self.session.scalars(
                select(Recurrence)
                .where(Recurrence.user_id == user_id, Recurrence.is_active.is_(True))
                .order_by(Recurrence.next_run_at)
            )
        )

    def get_recurrence(self, user_id: uuid.UUID, recurrence_id: uuid.UUID) -> Recurrence | None:
        return self.session.scalar(
            select(Recurrence).where(Recurrence.id == recurrence_id, Recurrence.user_id == user_id)
        )

    def commit(self) -> None:
        self.session.commit()

    def flush(self) -> None:
        self.session.flush()
