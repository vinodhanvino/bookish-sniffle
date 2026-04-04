from pathlib import Path

from app.config.database_session_provider import get_provider
from app.db.sales_upload import SalesUploadReport
from transormer.sales.lucid.pipeline.pipeline import run_etl


def _items_count(payload: dict) -> int:
    categories = payload.get("categories", [])
    total = 0
    for category in categories:
        total += len(category.get("items", []))
    return total


def ingest_sales_file(file_path: Path, source_name: str) -> dict:
    payload = run_etl(str(file_path))
    row = SalesUploadReport(source_file=source_name, payload=payload)
    get_provider().save(row)
    return {
        "source_file": source_name,
        "categories_count": len(payload.get("categories", [])),
        "items_count": _items_count(payload),
    }
