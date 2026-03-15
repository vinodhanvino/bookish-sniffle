"""JSON and JSONL file reader. Stream JSONL with iter_rows() for large files."""

import json
from pathlib import Path
from typing import Any, Iterator

from . import settings
from .base import BaseFileReader


class JsonReader(BaseFileReader):
    """Read JSON or JSONL. Use iter_rows() for large JSONL."""

    extensions = settings.EXT_JSON

    def iter_rows(self, path: str | Path) -> Iterator[dict[str, Any]]:
        path = Path(path)
        if path.suffix.lower() != ".jsonl":
            raise ValueError("iter_rows() only supports .jsonl files")
        with self._open_text(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def read(self, path: str | Path) -> Any:
        path = Path(path)
        with self._open_text(path) as f:
            if path.suffix.lower() == ".jsonl":
                return list(self.iter_rows(path))
            return json.load(f)
