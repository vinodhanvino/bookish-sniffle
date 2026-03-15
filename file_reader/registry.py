"""Registry to get the appropriate reader by file path or extension."""

from pathlib import Path
from typing import Iterator, Type

from . import settings
from .base import BaseFileReader
from .csv_reader import CsvReader
from .excel_reader import ExcelReader
from .json_reader import JsonReader
from .text_reader import TextReader
from .xml_reader import XmlReader
from .yaml_reader import YamlReader

_READERS: list[Type[BaseFileReader]] = [
    CsvReader,
    JsonReader,
    ExcelReader,
    XmlReader,
    YamlReader,
    TextReader,
]


def get_reader(path: str | Path) -> BaseFileReader | None:
    """Return a reader instance that supports the file, or None."""
    ext = Path(path).suffix.lower()
    for reader_cls in _READERS:
        if ext in reader_cls.extensions:
            return reader_cls()
    return None


def read_file(path: str | Path, reader: BaseFileReader | None = None) -> object:
    """Read file using auto-detected or provided reader."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    r = reader or get_reader(path)
    if r is None:
        raise ValueError(f"No reader for extension: {path.suffix}")
    return r.read(path)


def iter_file(
    path: str | Path, reader: BaseFileReader | None = None
) -> Iterator[dict]:
    """Stream rows one-by-one. O(1) memory. Use for CSV, JSONL, Excel."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    r = reader or get_reader(path)
    if r is None:
        raise ValueError(f"No reader for extension: {path.suffix}")
    try:
        yield from r.iter_rows(path)
    except NotImplementedError as e:
        raise ValueError(
            f"Streaming not supported for {path.suffix}; use read_file()"
        ) from e


def read_chunked(
    path: str | Path,
    chunk_size: int | None = None,
    reader: BaseFileReader | None = None,
) -> Iterator[list[dict]]:
    """Yield chunks of rows. O(chunk_size) memory. For CSV, JSONL, Excel."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    r = reader or get_reader(path)
    if r is None:
        raise ValueError(f"No reader for extension: {path.suffix}")
    size = chunk_size or settings.DEFAULT_CHUNK_SIZE
    chunk: list[dict] = []
    try:
        for row in r.iter_rows(path):
            chunk.append(row)
            if len(chunk) >= size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk
    except NotImplementedError as e:
        raise ValueError(
            f"Chunked read not supported for {path.suffix}; use read_file()"
        ) from e


def register_reader(reader_cls: Type[BaseFileReader]) -> None:
    """Register a custom reader (prepended to list)."""
    _READERS.insert(0, reader_cls)
