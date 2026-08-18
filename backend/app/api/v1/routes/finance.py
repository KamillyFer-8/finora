import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import CurrentUser, SessionDep
from app.repositories.finance import FinanceRepository
from app.schemas.finance import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    CategoryCreate,
    CategoryResponse,
    RecurrenceCreate,
    RecurrenceResponse,
    TransactionCreate,
    TransactionPage,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.finance import FinanceService

accounts_router = APIRouter(prefix="/accounts", tags=["accounts"])
categories_router = APIRouter(prefix="/categories", tags=["categories"])
transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])
recurrences_router = APIRouter(prefix="/recurrences", tags=["recurrences"])


def service(session: SessionDep, user: CurrentUser) -> FinanceService:
    return FinanceService(FinanceRepository(session), user.id)


@accounts_router.get("", response_model=list[AccountResponse])
def list_accounts(session: SessionDep, user: CurrentUser) -> list[AccountResponse]:
    return [
        AccountResponse.model_validate(item)
        for item in FinanceRepository(session).list_accounts(user.id)
    ]


@accounts_router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate, session: SessionDep, user: CurrentUser
) -> AccountResponse:
    return AccountResponse.model_validate(service(session, user).create_account(payload))


@accounts_router.patch("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: uuid.UUID, payload: AccountUpdate, session: SessionDep, user: CurrentUser
) -> AccountResponse:
    return AccountResponse.model_validate(
        service(session, user).update_account(account_id, payload)
    )


@accounts_router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: uuid.UUID, session: SessionDep, user: CurrentUser) -> Response:
    service(session, user).delete_account(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@categories_router.get("", response_model=list[CategoryResponse])
def list_categories(
    session: SessionDep, user: CurrentUser, type: Literal["income", "expense"] | None = None
) -> list[CategoryResponse]:
    return [
        CategoryResponse.model_validate(item)
        for item in FinanceRepository(session).list_categories(user.id, type)
    ]


@categories_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate, session: SessionDep, user: CurrentUser
) -> CategoryResponse:
    return CategoryResponse.model_validate(service(session, user).create_category(payload))


@transactions_router.get("", response_model=TransactionPage)
def list_transactions(
    session: SessionDep,
    user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: str | None = None,
    type: Literal["income", "expense"] | None = None,
    status_: Annotated[
        Literal["pending", "completed", "cancelled"] | None, Query(alias="status")
    ] = None,
    account_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sort: Literal["date_desc", "date_asc", "amount_desc", "amount_asc"] = "date_desc",
) -> TransactionPage:
    items, total = FinanceRepository(session).list_transactions(
        user.id,
        page=page,
        page_size=page_size,
        search=search,
        type_=type,
        status=status_,
        account_id=account_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        sort=sort,
    )
    return TransactionPage(
        items=[TransactionResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@transactions_router.post(
    "", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
def create_transaction(
    payload: TransactionCreate, session: SessionDep, user: CurrentUser
) -> TransactionResponse:
    return TransactionResponse.model_validate(service(session, user).create_transaction(payload))


@transactions_router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: uuid.UUID, payload: TransactionUpdate, session: SessionDep, user: CurrentUser
) -> TransactionResponse:
    return TransactionResponse.model_validate(
        service(session, user).update_transaction(transaction_id, payload)
    )


@transactions_router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: uuid.UUID, session: SessionDep, user: CurrentUser
) -> Response:
    service(session, user).delete_transaction(transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@transactions_router.post(
    "/{transaction_id}/duplicate",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def duplicate_transaction(
    transaction_id: uuid.UUID, session: SessionDep, user: CurrentUser
) -> TransactionResponse:
    return TransactionResponse.model_validate(
        service(session, user).duplicate_transaction(transaction_id)
    )


@recurrences_router.get("", response_model=list[RecurrenceResponse])
def list_recurrences(session: SessionDep, user: CurrentUser) -> list[RecurrenceResponse]:
    items = FinanceRepository(session).list_recurrences(user.id)
    return [RecurrenceResponse.model_validate(item) for item in items]


@recurrences_router.post(
    "", response_model=RecurrenceResponse, status_code=status.HTTP_201_CREATED
)
def create_recurrence(
    payload: RecurrenceCreate, session: SessionDep, user: CurrentUser
) -> RecurrenceResponse:
    recurrence = service(session, user).create_recurrence(payload)
    return RecurrenceResponse.model_validate(recurrence)


@recurrences_router.delete("/{recurrence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurrence(recurrence_id: uuid.UUID, session: SessionDep, user: CurrentUser) -> Response:
    service(session, user).delete_recurrence(recurrence_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
