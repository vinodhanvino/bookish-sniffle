"""Base file reader interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterator

from . import settings


class BaseFileReader(ABC):
    """Abstract base for all file readers."""

    extensions: tuple[str, ...] = ()

    def __init__(
        self,
        encoding: str | None = None,
        **kwargs: Any,
    ):
        self.encoding = encoding or settings.DEFAULT_ENCODING
        self._kwargs = kwargs

    def supports(self, path: str | Path) -> bool:
        """Return True if this reader supports the file extension."""
        ext = Path(path).suffix.lower()
        return ext in self.extensions

    @abstractmethod
    def read(self, path: str | Path) -> Any:
        """Read file and return parsed content. Prefer iter_rows() for huge files."""
        raise NotImplementedError

    def iter_rows(self, path: str | Path) -> Iterator[dict[str, Any]]:
        """Stream rows one-by-one. Override for tabular formats. O(1) memory."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support streaming; use read() for small files."
        )

    def _open_text(self, path: str | Path, mode: str = "r"):
        return open(
            path,
            mode,
            encoding=self.encoding,
            buffering=settings.FILE_READ_BUFFER_BYTES,
        )

    def _open_binary(self, path: str | Path, mode: str = "rb"):
        return open(path, mode, buffering=settings.FILE_READ_BUFFER_BYTES)
