"""
validator.py
------------
Business-rule validation functions that check numeric consistency and
flag suspicious data.  All functions are pure (no side-effects) and
return lists of human-readable warning strings rather than raising
exceptions, so the pipeline can always produce a result and let the
caller decide how to handle anomalies.

Public API
----------
validate_item_total(item)             -> list[str]
validate_category_total(category)     -> list[str]
validate_report_total(report)         -> list[str]
validate_no_negative_sales(category)  -> list[str]
validate_suspicious_prices(category)  -> list[str]
"""

from __future__ import annotations

from typing import List

from .models import SalesCategory, SalesItem, SalesReport


# ---------------------------------------------------------------------------
# Tolerance used for floating-point comparisons
# ---------------------------------------------------------------------------

_CURRENCY_TOLERANCE = 0.02   # ±2 paise / cents
_SUSPICIOUS_PRICE_THRESHOLD = 1.0   # unit prices below this are flagged


# ---------------------------------------------------------------------------
# Item-level validation
# ---------------------------------------------------------------------------

def validate_item_total(item: SalesItem) -> List[str]:
    """
    Check that ``unit_price × quantity`` equals the recorded ``total_price``.

    Parameters
    ----------
    item : SalesItem

    Returns
    -------
    list of str
        Empty when the item passes validation.
        Contains one warning string when the computed and recorded totals
        differ by more than ``_CURRENCY_TOLERANCE``.
    """
    computed = round(item.unit_price * item.quantity, 2)
    if abs(computed - item.total_price) > _CURRENCY_TOLERANCE:
        return [
            f"'{item.product_name}': computed total {computed:.2f} "
            f"!= recorded total {item.total_price:.2f}"
        ]
    return []


# ---------------------------------------------------------------------------
# Category-level validation
# ---------------------------------------------------------------------------

def validate_category_total(category: SalesCategory) -> List[str]:
    """
    Verify that the sum of all item ``total_price`` values equals
    ``category.total_category_sales``.

    Parameters
    ----------
    category : SalesCategory

    Returns
    -------
    list of str
        Empty when the category total is consistent.
    """
    computed_sum = round(sum(item.total_price for item in category.items), 2)
    if abs(computed_sum - category.total_category_sales) > _CURRENCY_TOLERANCE:
        return [
            f"Category '{category.category_name}': sum of items "
            f"({computed_sum:.2f}) != category total "
            f"({category.total_category_sales:.2f})"
        ]
    return []


def validate_no_negative_sales(category: SalesCategory) -> List[str]:
    """
    Flag any items with a negative ``total_price`` that are not explicitly
    marked as returns (no return-marker convention exists in this dataset).

    Parameters
    ----------
    category : SalesCategory

    Returns
    -------
    list of str
    """
    warnings: List[str] = []
    for item in category.items:
        if item.total_price < 0:
            warnings.append(
                f"'{item.product_name}' in '{category.category_name}' has "
                f"negative total_price ({item.total_price:.2f}). "
                "Mark as a return if intentional."
            )
    return warnings


def validate_suspicious_prices(category: SalesCategory) -> List[str]:
    """
    Flag items whose ``unit_price`` is suspiciously low (below
    ``_SUSPICIOUS_PRICE_THRESHOLD``), which may indicate complimentary
    or internally-tracked entries rather than real revenue.

    Parameters
    ----------
    category : SalesCategory

    Returns
    -------
    list of str
    """
    warnings: List[str] = []
    for item in category.items:
        if 0 < item.unit_price < _SUSPICIOUS_PRICE_THRESHOLD:
            warnings.append(
                f"'{item.product_name}' (menu: '{item.menu}') has a very low "
                f"unit_price of {item.unit_price:.4f} — likely a complimentary "
                "or internal tracking entry, not real revenue."
            )
    return warnings


# ---------------------------------------------------------------------------
# Report-level validation
# ---------------------------------------------------------------------------

def validate_report_total(report: SalesReport) -> List[str]:
    """
    Verify that the sum of all ``category.total_category_sales`` values
    equals ``report.total_sales``.

    Parameters
    ----------
    report : SalesReport

    Returns
    -------
    list of str
        Empty when the grand total is consistent.
    """
    computed_sum = round(
        sum(cat.total_category_sales for cat in report.categories), 2
    )
    if abs(computed_sum - report.total_sales) > _CURRENCY_TOLERANCE:
        return [
            f"Grand total mismatch: sum of categories ({computed_sum:.2f}) "
            f"!= report total_sales ({report.total_sales:.2f})"
        ]
    return []