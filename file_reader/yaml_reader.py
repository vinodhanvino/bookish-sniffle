"""YAML file reader."""

from pathlib import Path
from typing import Any

from . import settings
from .base import BaseFileReader


class YamlReader(BaseFileReader):
    """Read YAML files. Returns dict/list structure."""

    extensions = settings.EXT_YAML

    def read(self, path: str | Path) -> Any:
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required: pip install pyyaml")

        with self._open_text(path) as f:
            return yaml.safe_load(f) or {}
