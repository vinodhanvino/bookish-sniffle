"""
transformer.py
--------------
Converts a clean pandas DataFrame (from ``cleaner.clean``) into the
domain model hierarchy defined in ``models.py``:

    DataFrame  →  [SalesItem]  →  [SalesCategory]  →  SalesReport

All validation warnings are attached inline to the objects they concern,
using the functions in ``validator.py``.

Public API
----------
build_sales_item(row, sale_date)         -> SalesItem
build_sales_category(name, group_df)     -> SalesCategory
build_sales_report(clean_df, metadata)   -> SalesReport
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from .cleaner import (
    COL_CLASSIFICATION,
    COL_ITEM_NAME,
    COL_MENU,
    COL_QTY,
    COL_RATE,
    COL_TOTAL_AMOUNT,
)
from .models import SalesCategory, SalesItem, SalesReport
from .validator import (
    validate_category_total,
    validate_item_total,
    validate_no_negative_sales,
    validate_report_total,
    validate_suspicious_prices,
)


# ---------------------------------------------------------------------------
# Row → SalesItem
# ---------------------------------------------------------------------------

def build_sales_item(row: pd.Series, sale_date: str) -> SalesItem:
    """
    Construct a validated ``SalesItem`` from a single DataFrame row.

    The ``sale_date`` is the ISO-8601 start date parsed from the report
    header (not stored per-row in the source file).

    Parameters
    ----------
    row : pd.Series
        A single row from the cleaned DataFrame.
    sale_date : str
        ISO-8601 date string, e.g. ``"2016-02-09"``.

    Returns
    -------
    SalesItem
        Item with ``warnings`` populated if the line-total is inconsistent.
    """
    item = SalesItem(
        product_name=str(row[COL_ITEM_NAME]),
        quantity=float(row[COL_QTY]),
        unit_price=float(row[COL_RATE]),
        total_price=float(row[COL_TOTAL_AMOUNT]),
        date=sale_date,
        menu=str(row[COL_MENU]),
    )
    item.warnings = validate_item_total(item)
    return item


# ---------------------------------------------------------------------------
# DataFrame group → SalesCategory
# ---------------------------------------------------------------------------

def build_sales_category(
    category_name: str,
    group_df: pd.DataFrame,
    sale_date: str,
) -> SalesCategory:
    """
    Build a ``SalesCategory`` from a subset of the cleaned DataFrame that
    all share the same ``Classification`` value.

    Parameters
    ----------
    category_name : str
        The classification label (e.g. ``"Food"``, ``"Liquor"``).
    group_df : pd.DataFrame
        All rows belonging to this category.
    sale_date : str
        ISO-8601 date string forwarded to each ``SalesItem``.

    Returns
    -------
    SalesCategory
        Category with items built and validation warnings attached.
    """
    items = [
        build_sales_item(row, sale_date)
        for _, row in group_df.iterrows()
    ]

    total_category_sales = round(float(group_df[COL_TOTAL_AMOUNT].sum()), 2)

    category = SalesCategory(
        category_name=category_name,
        total_category_sales=total_category_sales,
        items=items,
    )

    category.warnings = (
        validate_category_total(category)
        + validate_no_negative_sales(category)
        + validate_suspicious_prices(category)
    )

    return category


# ---------------------------------------------------------------------------
# Full DataFrame → SalesReport
# ---------------------------------------------------------------------------

def build_sales_report(
    clean_df: pd.DataFrame,
    metadata: Dict[str, str],
) -> SalesReport:
    """
    Assemble a complete ``SalesReport`` from the cleaned DataFrame and the
    metadata dict returned by ``reader.extract_report_metadata``.

    The function groups rows by ``Classification``, builds one
    ``SalesCategory`` per group, then wraps everything in a ``SalesReport``
    with the grand-total validation applied.

    Parameters
    ----------
    clean_df : pd.DataFrame
        Fully cleaned DataFrame from ``cleaner.clean``.
    metadata : dict
        Must contain keys ``"date_range"`` and ``"restaurant"``.
        Produced by ``reader.extract_report_metadata``.

    Returns
    -------
    SalesReport
        Complete, validated sales report domain object.
    """
    date_range = metadata["date_range"]
    restaurant = metadata["restaurant"]
    sale_date  = date_range.split("/")[0]          # start date of range

    categories = [
        build_sales_category(classification, group_df, sale_date)
        for classification, group_df in clean_df.groupby(COL_CLASSIFICATION)
    ]

    total_sales = round(float(clean_df[COL_TOTAL_AMOUNT].sum()), 2)

    report = SalesReport(
        date_range=date_range,
        restaurant=restaurant,
        total_sales=total_sales,
        categories=categories,
    )

    report.warnings = validate_report_total(report)

    return report