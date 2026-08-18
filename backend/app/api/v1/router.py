from fastapi import APIRouter

from app.api.v1.routes.attachments import router as attachments_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.credit import cards_router, invoices_router
from app.api.v1.routes.finance import (
    accounts_router,
    categories_router,
    recurrences_router,
    transactions_router,
)
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.planning import alerts_router, budgets_router, goals_router
from app.api.v1.routes.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(accounts_router)
api_router.include_router(categories_router)
api_router.include_router(transactions_router)
api_router.include_router(recurrences_router)
api_router.include_router(cards_router)
api_router.include_router(invoices_router)
api_router.include_router(budgets_router)
api_router.include_router(goals_router)
api_router.include_router(alerts_router)
api_router.include_router(reports_router)
api_router.include_router(attachments_router)
api_router.include_router(health_router)
