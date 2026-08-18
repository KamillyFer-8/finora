import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.credit import Card, CardInstallment, CardPurchase, Invoice


class CreditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, model: object) -> None:
        self.session.add(model)

    def get_card(self, user_id: uuid.UUID, card_id: uuid.UUID) -> Card | None:
        return self.session.scalar(
            select(Card).where(
                Card.id == card_id, Card.user_id == user_id, Card.is_active.is_(True)
            )
        )

    def list_cards(self, user_id: uuid.UUID) -> list[Card]:
        return list(
            self.session.scalars(
                select(Card)
                .where(Card.user_id == user_id, Card.is_active.is_(True))
                .order_by(Card.created_at)
            )
        )

    def used_limit(self, user_id: uuid.UUID, card_id: uuid.UUID) -> Decimal:
        return self.session.scalar(
            select(func.coalesce(func.sum(Invoice.total), 0)).where(
                Invoice.user_id == user_id, Invoice.card_id == card_id, Invoice.status != "paid"
            )
        ) or Decimal("0")

    def current_invoice_total(self, user_id: uuid.UUID, card_id: uuid.UUID) -> Decimal:
        invoice = self.session.scalar(
            select(Invoice)
            .where(
                Invoice.user_id == user_id,
                Invoice.card_id == card_id,
                Invoice.status.in_(["open", "closed", "overdue"]),
            )
            .order_by(Invoice.due_date)
            .limit(1)
        )
        return invoice.total if invoice else Decimal("0")

    def get_invoice_by_month(
        self, user_id: uuid.UUID, card_id: uuid.UUID, month: date
    ) -> Invoice | None:
        return self.session.scalar(
            select(Invoice).where(
                Invoice.user_id == user_id,
                Invoice.card_id == card_id,
                Invoice.reference_month == month,
            )
        )

    def get_invoice(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> Invoice | None:
        return self.session.scalar(
            select(Invoice)
            .options(
                selectinload(Invoice.installments).selectinload(CardInstallment.purchase),
                selectinload(Invoice.card),
            )
            .where(Invoice.id == invoice_id, Invoice.user_id == user_id)
        )

    def list_invoices(
        self, user_id: uuid.UUID, card_id: uuid.UUID | None = None, status: str | None = None
    ) -> list[Invoice]:
        query = (
            select(Invoice)
            .options(
                selectinload(Invoice.installments).selectinload(CardInstallment.purchase),
                selectinload(Invoice.card),
            )
            .where(Invoice.user_id == user_id)
        )
        if card_id:
            query = query.where(Invoice.card_id == card_id)
        if status:
            query = query.where(Invoice.status == status)
        return list(self.session.scalars(query.order_by(Invoice.due_date.desc())))

    def list_purchases(self, user_id: uuid.UUID, card_id: uuid.UUID) -> list[CardPurchase]:
        return list(
            self.session.scalars(
                select(CardPurchase)
                .options(selectinload(CardPurchase.installments))
                .where(CardPurchase.user_id == user_id, CardPurchase.card_id == card_id)
                .order_by(CardPurchase.purchase_date.desc())
            )
        )

    def commit(self) -> None:
        self.session.commit()

    def flush(self) -> None:
        self.session.flush()
