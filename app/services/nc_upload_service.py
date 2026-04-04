from pathlib import Path

from app.config.database_session_provider import get_provider
from app.db.nc_upload import NcUploadRow
from file_reader.excel_reader import ExcelReader


def _normalize(row: dict) -> dict:
    clean: dict = {}
    for k, v in row.items():
        key = str(k).strip() if k is not None else ""
        if not key:
            continue
        clean[key] = v
    return clean


def ingest_nc_file(file_path: Path, source_name: str) -> dict:
    rows = ExcelReader().read(file_path)
    payload_rows = [_normalize(row) for row in rows]
    to_insert = [
        NcUploadRow(source_file=source_name, row_index=i + 1, payload=row)
        for i, row in enumerate(payload_rows)
    ]

    if to_insert:
        get_provider().save_all(to_insert)

    return {
        "source_file": source_name,
        "rows_read": len(rows),
        "rows_inserted": len(to_insert),
    }
