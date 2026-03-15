"""XML file reader."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from . import settings
from .base import BaseFileReader


class XmlReader(BaseFileReader):
    """Read XML files. Returns root Element or parsed dict-like structure."""

    extensions = settings.EXT_XML

    def __init__(
        self,
        encoding: str | None = None,
        as_dict: bool = False,
        **kwargs: Any,
    ):
        super().__init__(encoding=encoding, **kwargs)
        self.as_dict = as_dict

    def read(self, path: str | Path) -> Any:
        tree = ET.parse(path)
        root = tree.getroot()
        if self.as_dict:
            return self._element_to_dict(root)
        return root

    def _element_to_dict(self, element: ET.Element) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if element.attrib:
            result["@attributes"] = dict(element.attrib)
        if element.text and element.text.strip():
            result["#text"] = element.text.strip()
        for child in element:
            child_data = self._element_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        return result
