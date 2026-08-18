import uuid
from typing import Literal

from fastapi import APIRouter, Response, status

from app.api.dependencies import CurrentUser, SessionDep
from app.models.credit import Card, Invoice
from app.repositories.credit import CreditRepository
from app.repositories.finance import FinanceRepository
from app.schemas.credit import (
    CardCreate,
    CardResponse,
    CardUpdate,
    InstallmentResponse,
    InvoicePayment,
    InvoiceResponse,
    PurchaseCreate,
    PurchaseResponse,
)
from app.services.credit import CreditService

cards_router = APIRouter(prefix="/cards", tags=["cards"])
invoices_router = APIRouter(prefix="/invoices", tags=["invoices"])


def service(session: SessionDep, user: CurrentUser) -> CreditService:
    return CreditService(CreditRepository(session), FinanceRepository(session), user.id)


def card_response(card: Card, repository: CreditRepository, user_id: uuid.UUID) -> CardResponse:
    used = repository.used_limit(user_id, card.id)
    return CardResponse.model_validate(
        {
            **card.__dict__,
            "used_limit": used,
            "available_limit": card.credit_limit - used,
            "current_invoice": repository.current_invoice_total(user_id, card.id),
        }
    )


def invoice_response(invoice: Invoice) -> InvoiceResponse:
    return InvoiceResponse(
        id=invoice.id,
        card_id=invoice.card_id,
        card_name=invoice.card.name,
        reference_month=invoice.reference_month,
        closing_date=invoice.closing_date,
        due_date=invoice.due_date,
        total=invoice.total,
        status=invoice.status,
        installments=[
            InstallmentResponse(
                id=item.id,
                purchase_id=item.purchase_id,
                number=item.number,
                amount=item.amount,
                description=item.purchase.description,
                installment_count=item.purchase.installment_count,
            )
            for item in invoice.installments
        ],
    )


@cards_router.get("", response_model=list[CardResponse])
def list_cards(session: SessionDep, user: CurrentUser) -> list[CardResponse]:
    repository = CreditRepository(session)
    return [card_response(card, repository, user.id) for card in repository.list_cards(user.id)]


@cards_router.post("", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(payload: CardCreate, session: SessionDep, user: CurrentUser) -> CardResponse:
    repository = CreditRepository(session)
    card = CreditService(repository, FinanceRepository(session), user.id).create_card(payload)
    return card_response(card, repository, user.id)


@cards_router.patch("/{card_id}", response_model=CardResponse)
def update_card(
    card_id: uuid.UUID, payload: CardUpdate, session: SessionDep, user: CurrentUser
) -> CardResponse:
    repository = CreditRepository(session)
    card = CreditService(repository, FinanceRepository(session), user.id).update_card(
        card_id, payload
    )
    return card_response(card, repository, user.id)


@cards_router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: uuid.UUID, session: SessionDep, user: CurrentUser) -> Response:
    service(session, user).delete_card(card_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@cards_router.post(
    "/{card_id}/purchases", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED
)
def create_purchase(
    card_id: uuid.UUID, payload: PurchaseCreate, session: SessionDep, user: CurrentUser
) -> PurchaseResponse:
    return PurchaseResponse.model_validate(service(session, user).create_purchase(card_id, payload))


@cards_router.get("/{card_id}/purchases", response_model=list[PurchaseResponse])
def list_purchases(
    card_id: uuid.UUID, session: SessionDep, user: CurrentUser
) -> list[PurchaseResponse]:
    service(session, user)._card(card_id)
    return [
        PurchaseResponse.model_validate(item)
        for item in CreditRepository(session).list_purchases(user.id, card_id)
    ]


@invoices_router.get("", response_model=list[InvoiceResponse])
def list_invoices(
    session: SessionDep,
    user: CurrentUser,
    card_id: uuid.UUID | None = None,
    status_: Literal["open", "closed", "paid", "overdue"] | None = None,
) -> list[InvoiceResponse]:
    repository = CreditRepository(session)
    invoices = repository.list_invoices(user.id, card_id, status_)
    service(session, user).sync_overdue(invoices)
    return [invoice_response(item) for item in invoices]


@invoices_router.post("/{invoice_id}/close", response_model=InvoiceResponse)
def close_invoice(invoice_id: uuid.UUID, session: SessionDep, user: CurrentUser) -> InvoiceResponse:
    return invoice_response(service(session, user).close_invoice(invoice_id))


@invoices_router.post("/{invoice_id}/pay", response_model=InvoiceResponse)
def pay_invoice(
    invoice_id: uuid.UUID, payload: InvoicePayment, session: SessionDep, user: CurrentUser
) -> InvoiceResponse:
    return invoice_response(service(session, user).pay_invoice(invoice_id, payload.account_id))
