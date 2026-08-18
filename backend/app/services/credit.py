import calendar
import uuid
from datetime import UTC, date, datetime
from decimal import ROUND_DOWN, Decimal

from fastapi import HTTPException, status

from app.models.credit import Card, CardInstallment, CardPurchase, Invoice
from app.repositories.credit import CreditRepository
from app.repositories.finance import FinanceRepository
from app.schemas.credit import CardCreate, CardUpdate, PurchaseCreate


def add_months(value: date, months: int) -> date:
    index = value.year * 12 + value.month - 1 + months
    year, month_index = divmod(index, 12)
    return date(
        year, month_index + 1, min(value.day, calendar.monthrange(year, month_index + 1)[1])
    )


class CreditService:
    def __init__(
        self, repository: CreditRepository, finance: FinanceRepository, user_id: uuid.UUID
    ) -> None:
        self.repository = repository
        self.finance = finance
        self.user_id = user_id

    def create_card(self, data: CardCreate) -> Card:
        card = Card(user_id=self.user_id, **data.model_dump())
        self.repository.add(card)
        self.repository.commit()
        return card

    def update_card(self, card_id: uuid.UUID, data: CardUpdate) -> Card:
        card = self._card(card_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(card, key, value)
        if card.credit_limit < self.repository.used_limit(self.user_id, card.id):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Limite inferior ao valor utilizado"
            )
        self.repository.commit()
        return card

    def delete_card(self, card_id: uuid.UUID) -> None:
        card = self._card(card_id)
        if self.repository.used_limit(self.user_id, card.id) > 0:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Quite as faturas antes de excluir o cartão"
            )
        card.is_active = False
        self.repository.commit()

    def create_purchase(self, card_id: uuid.UUID, data: PurchaseCreate) -> CardPurchase:
        card = self._card(card_id)
        available = card.credit_limit - self.repository.used_limit(self.user_id, card.id)
        if data.total_amount > available:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Limite insuficiente")
        purchase = CardPurchase(user_id=self.user_id, card_id=card.id, **data.model_dump())
        self.repository.add(purchase)
        self.repository.flush()
        base_due = add_months(
            date(data.purchase_date.year, data.purchase_date.month, 1),
            1 if data.purchase_date.day <= card.closing_day else 2,
        )
        regular = (data.total_amount / data.installment_count).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )
        allocated = Decimal("0")
        for index in range(data.installment_count):
            reference = add_months(base_due, index)
            invoice = self.repository.get_invoice_by_month(self.user_id, card.id, reference)
            if not invoice:
                closing_month = add_months(reference, -1)
                invoice = Invoice(
                    user_id=self.user_id,
                    card_id=card.id,
                    reference_month=reference,
                    closing_date=date(closing_month.year, closing_month.month, card.closing_day),
                    due_date=date(reference.year, reference.month, card.due_day),
                    total=Decimal("0"),
                    status="open",
                )
                self.repository.add(invoice)
                self.repository.flush()
            amount = (
                data.total_amount - allocated if index == data.installment_count - 1 else regular
            )
            allocated += amount
            invoice.total += amount
            self.repository.add(
                CardInstallment(
                    purchase_id=purchase.id, invoice_id=invoice.id, number=index + 1, amount=amount
                )
            )
        self.repository.commit()
        return purchase

    def close_invoice(self, invoice_id: uuid.UUID) -> Invoice:
        invoice = self._invoice(invoice_id)
        if invoice.status != "open":
            raise HTTPException(status.HTTP_409_CONFLICT, "Fatura não está aberta")
        invoice.status = "closed"
        self.repository.commit()
        return invoice

    def pay_invoice(self, invoice_id: uuid.UUID, account_id: uuid.UUID) -> Invoice:
        invoice = self._invoice(invoice_id)
        if invoice.status == "paid":
            raise HTTPException(status.HTTP_409_CONFLICT, "Fatura já está paga")
        account = self.finance.get_account(self.user_id, account_id)
        if not account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conta não encontrada")
        if account.balance < invoice.total:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Saldo insuficiente")
        account.balance -= invoice.total
        invoice.status = "paid"
        invoice.paid_at = datetime.now(UTC)
        self.repository.commit()
        return invoice

    def sync_overdue(self, invoices: list[Invoice]) -> None:
        changed = False
        for invoice in invoices:
            if invoice.status in {"open", "closed"} and invoice.due_date < date.today():
                invoice.status = "overdue"
                changed = True
        if changed:
            self.repository.commit()

    def _card(self, card_id: uuid.UUID) -> Card:
        card = self.repository.get_card(self.user_id, card_id)
        if not card:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Cartão não encontrado")
        return card

    def _invoice(self, invoice_id: uuid.UUID) -> Invoice:
        invoice = self.repository.get_invoice(self.user_id, invoice_id)
        if not invoice:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Fatura não encontrada")
        return invoice
