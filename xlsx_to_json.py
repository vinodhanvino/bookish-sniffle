"""Read all xlsx under source dir with ExcelReader and write combined JSON to processed dir."""

import json
import sys
from datetime import date, datetime
from pathlib import Path

try:
    from .file_reader import ExcelReader
    from .file_reader.settings import (
        NAME_COLUMNS_FOR_QTY,
        PROCESSED_JSON_FILENAME,
        PROCESSED_OUTPUT_DIR,
        XLSX_SOURCE_DIR,
    )
    from .product_qty_parser import extract_qty_from_name
except ImportError:
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from be.file_reader import ExcelReader
    from be.file_reader.settings import (
        NAME_COLUMNS_FOR_QTY,
        PROCESSED_JSON_FILENAME,
        PROCESSED_OUTPUT_DIR,
        XLSX_SOURCE_DIR,
    )
    from be.product_qty_parser import extract_qty_from_name


def _json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _collect_xlsx_paths(source_dir: Path) -> list[Path]:
    return sorted(source_dir.glob("*.xlsx"))


def _row_with_qty(row: dict, name_columns: tuple[str, ...]) -> dict:
    name_val = None
    for key in name_columns:
        if key in row:
            name_val = row[key]
            break
    qty = extract_qty_from_name(str(name_val)) if name_val is not None else None
    return {**row, "qty": qty}


def combine_xlsx_to_json(
    source_dir: Path | None = None,
    output_dir: Path | None = None,
    output_filename: str | None = None,
) -> Path:
    source_dir = source_dir or XLSX_SOURCE_DIR
    output_dir = output_dir or PROCESSED_OUTPUT_DIR
    output_filename = output_filename or PROCESSED_JSON_FILENAME
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = _collect_xlsx_paths(source_dir)
    reader = ExcelReader()
    combined: list[dict] = []

    for path in paths:
        rows = reader.read(path)
        for row in rows:
            with_qty = _row_with_qty(row, NAME_COLUMNS_FOR_QTY)
            combined.append({"source": path.name, **with_qty})

    out_path = output_dir / output_filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {"files_count": len(paths), "rows_count": len(combined), "data": combined},
            f,
            ensure_ascii=False,
            indent=2,
            default=_json_serial,
        )
    return out_path



if __name__ == "__main__":
    base = Path(rf"D:\office\code\spirix resource\processed")
    combine_xlsx_to_json(
        source_dir=base,
        output_dir=base / "processed",
        output_filename="master-ksbcl.json",
    )