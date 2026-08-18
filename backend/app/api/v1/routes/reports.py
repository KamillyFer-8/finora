import csv
import io
from datetime import date

from fastapi import APIRouter, HTTPException, Response, status

from app.api.dependencies import CurrentUser, SessionDep
from app.repositories.planning import PlanningRepository
from app.repositories.reports import ReportsRepository
from app.schemas.reports import DashboardReport
from app.services.reports import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])


def resolve_period(start_date: date | None, end_date: date | None) -> tuple[date, date]:
    today = date.today()
    start = start_date or today.replace(day=1)
    end = end_date or today
    if end < start:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Período inválido")
    if (end - start).days > 1095:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Período máximo de três anos")
    return start, end


@router.get("/dashboard", response_model=DashboardReport)
def dashboard(
    session: SessionDep,
    user: CurrentUser,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DashboardReport:
    start, end = resolve_period(start_date, end_date)
    return ReportsService(
        ReportsRepository(session), PlanningRepository(session), user.id
    ).dashboard(start, end)


@router.get("/export.csv")
def export_csv(
    session: SessionDep,
    user: CurrentUser,
    start_date: date | None = None,
    end_date: date | None = None,
) -> Response:
    start, end = resolve_period(start_date, end_date)
    transactions = ReportsRepository(session).transactions(user.id, start, end)
    categories = ReportsRepository(session).categories(user.id)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Data", "Descrição", "Tipo", "Categoria", "Status", "Valor"])
    for item in transactions:
        writer.writerow(
            [
                item.date.isoformat(),
                item.description,
                "Receita" if item.type == "income" else "Despesa",
                categories[item.category_id].name
                if item.category_id in categories
                else "Sem categoria",
                item.status,
                f"{item.amount:.2f}",
            ]
        )
    content = "\ufeff" + output.getvalue()
    filename = f"finora-{start.isoformat()}-{end.isoformat()}.csv"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
