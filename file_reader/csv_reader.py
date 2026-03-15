"""CSV/TSV file reader. Streams row-by-row for O(1) memory on large files."""

import csv
from pathlib import Path
from typing import Any, Iterator

from . import settings
from .base import BaseFileReader


class CsvReader(BaseFileReader):
    """Read CSV and TSV. Use iter_rows() for millions of rows."""

    extensions = settings.EXT_CSV

    def __init__(
        self,
        encoding: str | None = None,
        delimiter: str | None = None,
        dialect: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(encoding=encoding, **kwargs)
        self.delimiter = delimiter or settings.CSV_DELIMITER
        self.dialect = dialect or settings.CSV_DIALECT

    def iter_rows(self, path: str | Path) -> Iterator[dict[str, Any]]:
        path = Path(path)
        with self._open_text(path) as f:
            if path.suffix.lower() == ".tsv":
                reader = csv.DictReader(f, delimiter="\t")
            else:
                reader = csv.DictReader(
                    f, delimiter=self.delimiter, dialect=self.dialect
                )
            yield from reader

    def read(self, path: str | Path) -> list[dict[str, Any]]:
        """Load all rows. Prefer iter_rows() for large files."""
        return list(self.iter_rows(path))
