# Backend

Requer Python 3.12+. Crie um ambiente virtual e execute `pip install -e ".[dev]"`, depois `uvicorn app.main:app --reload`.

Validações: `ruff check .`, `ruff format --check .`, `mypy app` e `pytest`.
