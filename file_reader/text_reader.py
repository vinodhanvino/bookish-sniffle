"""Plain text file reader."""

from pathlib import Path

from . import settings
from .base import BaseFileReader


class TextReader(BaseFileReader):
    """Read plain text files. Returns string or list of lines."""

    extensions = settings.EXT_TEXT

    def __init__(
        self,
        encoding: str | None = None,
        as_lines: bool = False,
        **kwargs,
    ):
        super().__init__(encoding=encoding, **kwargs)
        self.as_lines = as_lines

    def read(self, path: str | Path) -> str | list[str]:
        with self._open_text(path) as f:
            if self.as_lines:
                return [line.rstrip("\n\r") for line in f]
            return f.read()
