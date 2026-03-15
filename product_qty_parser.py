"""Extract ML/MI volume number from product name into qty."""

import re

# Matches number + optional space + ML or MI (e.g. 750ML, 375 MI, 2000MLx6Btls)
QTY_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:ML|MI)", re.IGNORECASE)


def extract_qty_from_name(text: str) -> int | float | None:
    """First ML/MI volume in text as number, or None."""
    if not text or not isinstance(text, str):
        return None
    m = QTY_PATTERN.search(text)
    if not m:
        return None
    val = float(m.group(1))
    return int(val) if val == int(val) else val
