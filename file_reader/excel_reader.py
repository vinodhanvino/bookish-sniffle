"""Excel (xlsx/xls) file reader. Streams rows for O(1) memory on large sheets."""

from pathlib import Path
from typing import Any, Iterator

from . import settings
from .base import BaseFileReader


class ExcelReader(BaseFileReader):
    """Read Excel. Use iter_rows() for millions of rows."""

    extensions = settings.EXT_EXCEL

    def __init__(
        self,
        encoding: str | None = None,
        sheet_index: int | None = None,
        header_row: int | None = None,
        **kwargs: Any,
    ):
        super().__init__(encoding=encoding, **kwargs)
        self.sheet_index = (
            sheet_index if sheet_index is not None else settings.EXCEL_SHEET_INDEX
        )
        self.header_row = (
            header_row if header_row is not None else settings.EXCEL_HEADER_ROW
        )

    def iter_rows(self, path: str | Path) -> Iterator[dict[str, Any]]:
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl is required for Excel: pip install openpyxl")

        path = Path(path)
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        sheet = wb.worksheets[self.sheet_index]
        try:
            rows_iter = sheet.iter_rows(values_only=True)
            for _ in range(self.header_row):
                next(rows_iter, None)
            header_values = next(rows_iter, None)
            if header_values is None:
                return
            headers = [
                str(h) if h is not None else f"col_{i}"
                for i, h in enumerate(header_values)
            ]
            for row in rows_iter:
                if any(cell is not None for cell in row):
                    yield dict(zip(headers, row))
        finally:
            wb.close()

    def read(self, path: str | Path) -> list[dict[str, Any]]:
        """Load all rows. Prefer iter_rows() for large sheets."""
        return list(self.iter_rows(path))
