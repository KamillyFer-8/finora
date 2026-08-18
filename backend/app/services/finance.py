import uuid
from decimal import Decimal

from fastapi import HTTPException, status

from app.models.finance import Account, Category, Recurrence, Transaction
from app.repositories.finance import FinanceRepository
from app.schemas.finance import (
    AccountCreate,
    AccountUpdate,
    CategoryCreate,
    RecurrenceCreate,
    TransactionCreate,
    TransactionUpdate,
)


class FinanceService:
    def __init__(self, repository: FinanceRepository, user_id: uuid.UUID) -> None:
        self.repository = repository
        self.user_id = user_id

    def create_account(self, data: AccountCreate) -> Account:
        account = Account(user_id=self.user_id, **data.model_dump())
        self.repository.add(account)
        self.repository.commit()
        return account

    def update_account(self, account_id: uuid.UUID, data: AccountUpdate) -> Account:
        account = self._account(account_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(account, key, value)
        self.repository.commit()
        return account

    def delete_account(self, account_id: uuid.UUID) -> None:
        account = self._account(account_id)
        account.is_active = False
        self.repository.commit()

    def create_category(self, data: CategoryCreate) -> Category:
        category = Category(user_id=self.user_id, **data.model_dump())
        self.repository.add(category)
        self.repository.commit()
        return category

    def create_transaction(self, data: TransactionCreate) -> Transaction:
        account = self._account(data.account_id)
        self._validate_category(data.category_id, data.type)
        transaction = Transaction(user_id=self.user_id, **data.model_dump())
        self.repository.add(transaction)
        self._apply_balance(account, transaction, Decimal("1"))
        self.repository.commit()
        return transaction

    def update_transaction(self, transaction_id: uuid.UUID, data: TransactionUpdate) -> Transaction:
        transaction = self._transaction(transaction_id)
        old_account = self._account(transaction.account_id)
        self._apply_balance(old_account, transaction, Decimal("-1"))
        changes = data.model_dump(exclude_unset=True)
        for key, value in changes.items():
            setattr(transaction, key, value)
        new_account = self._account(transaction.account_id)
        self._validate_category(transaction.category_id, transaction.type)
        self._apply_balance(new_account, transaction, Decimal("1"))
        self.repository.commit()
        return transaction

    def delete_transaction(self, transaction_id: uuid.UUID) -> None:
        transaction = self._transaction(transaction_id)
        self._apply_balance(self._account(transaction.account_id), transaction, Decimal("-1"))
        self.repository.delete(transaction)
        self.repository.commit()

    def duplicate_transaction(self, transaction_id: uuid.UUID) -> Transaction:
        source = self._transaction(transaction_id)
        data = TransactionCreate(
            description=f"{source.description} (cópia)",
            amount=source.amount,
            type=source.type,
            account_id=source.account_id,
            category_id=source.category_id,
            date=source.date,
            status=source.status,
            notes=source.notes,
        )
        return self.create_transaction(data)

    def create_recurrence(self, data: RecurrenceCreate) -> Recurrence:
        self._account(data.account_id)
        self._validate_category(data.category_id, data.type)
        if data.end_date and data.end_date < data.next_run_at:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Data final inválida")
        recurrence = Recurrence(user_id=self.user_id, **data.model_dump())
        self.repository.add(recurrence)
        self.repository.commit()
        return recurrence

    def delete_recurrence(self, recurrence_id: uuid.UUID) -> None:
        recurrence = self.repository.get_recurrence(self.user_id, recurrence_id)
        if not recurrence:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Recorrência não encontrada")
        recurrence.is_active = False
        self.repository.commit()

    def _account(self, account_id: uuid.UUID) -> Account:
        account = self.repository.get_account(self.user_id, account_id)
        if not account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conta não encontrada")
        return account

    def _transaction(self, transaction_id: uuid.UUID) -> Transaction:
        transaction = self.repository.get_transaction(self.user_id, transaction_id)
        if not transaction:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Transação não encontrada")
        return transaction

    def _validate_category(self, category_id: uuid.UUID | None, type_: str) -> None:
        if category_id:
            category = self.repository.get_category(self.user_id, category_id)
            if not category or category.type != type_:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Categoria incompatível")

    @staticmethod
    def _apply_balance(account: Account, transaction: Transaction, multiplier: Decimal) -> None:
        if transaction.status == "completed":
            direction = Decimal("1") if transaction.type == "income" else Decimal("-1")
            account.balance += transaction.amount * direction * multiplier
