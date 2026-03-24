"""
reader.py
---------
Responsible for loading the raw Excel workbook and returning a tidy,
structured pandas DataFrame that downstream modules can work with.

The source spreadsheet has no conventional header row — row index 3
contains the column names embedded inside report metadata.  This module
hides that complexity from the rest of the library.

Public API
----------
load_raw_excel(filepath)          -> pd.DataFrame   (all rows, all columns)
extract_report_metadata(filepath) -> dict            (date_range, restaurant)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

import pandas as pd


# ---------------------------------------------------------------------------
# Internal constants
# ---------------------------------------------------------------------------

_EXPECTED_COLUMNS = [
    "ItemName",
    "Rate",
    "Qty",
    "TotalAmount",
    "Classification",
    "RestaurantName",
    "MenuName",
    "Category",
    "ItemType",
]

_SHEET_NAME = "Sheet1"

# Row indices inside the raw sheet (0-based) that carry report-level metadata.
_ROW_DATE_RANGE  = 0   # "Between 09-Feb-2016 And 10-Feb-2016"
_ROW_RESTAURANT  = 1   # "Watsons Bar and Restaurant"


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def load_raw_excel(filepath: str | Path) -> pd.DataFrame:
    """
    Read the itemwise sales Excel file and return a raw DataFrame.

    The sheet has no usable header on row 0; the actual column labels sit
    at row index 3 in the file.  This function reads the sheet without a
    header and manually assigns the expected column names.

    Parameters
    ----------
    filepath : str or Path
        Path to the .xlsx sales report file.

    Returns
    -------
    pd.DataFrame
        Raw DataFrame with columns:
        ItemName, Rate, Qty, TotalAmount, Classification,
        RestaurantName, MenuName, Category, ItemType.

    Raises
    ------
    FileNotFoundError
        If the given path does not point to an existing file.
    ValueError
        If the sheet does not contain the expected number of columns.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    raw_df = pd.read_excel(filepath, sheet_name=_SHEET_NAME, header=None)

    actual_col_count  = raw_df.shape[1]
    expected_col_count = len(_EXPECTED_COLUMNS)
    if actual_col_count != expected_col_count:
        raise ValueError(
            f"Expected {expected_col_count} columns, found {actual_col_count}. "
            "The sheet layout may have changed."
        )

    raw_df.columns = _EXPECTED_COLUMNS
    return raw_df


def extract_report_metadata(filepath: str | Path) -> Dict[str, str]:
    """
    Parse top-level report metadata from the Excel file header rows.

    Reads the date range and restaurant name that appear before the data
    table in the source sheet.

    Parameters
    ----------
    filepath : str or Path
        Path to the .xlsx sales report file.

    Returns
    -------
    dict with keys:
        - ``date_range``  : ISO date range string, e.g. ``"2016-02-09/2016-02-10"``
        - ``restaurant``  : Restaurant name string.
    """
    raw_df = load_raw_excel(filepath)

    date_range  = _parse_date_range(str(raw_df.iloc[_ROW_DATE_RANGE, 0]))
    restaurant  = str(raw_df.iloc[_ROW_RESTAURANT, 0]).strip()

    return {"date_range": date_range, "restaurant": restaurant}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _parse_date_range(raw_text: str) -> str:
    """
    Convert a human-readable date range string to ISO-8601 format.

    Example input : ``"Between 09-Feb-2016 And 10-Feb-2016"``
    Example output: ``"2016-02-09/2016-02-10"``

    Falls back to the original text if no dates can be extracted.
    """
    matches = re.findall(r"\d{2}-[A-Za-z]{3}-\d{4}", raw_text)
    if len(matches) < 2:
        return raw_text.strip()

    start = pd.to_datetime(matches[0], format="%d-%b-%Y").strftime("%Y-%m-%d")
    end   = pd.to_datetime(matches[1], format="%d-%b-%Y").strftime("%Y-%m-%d")
    return f"{start}/{end}"