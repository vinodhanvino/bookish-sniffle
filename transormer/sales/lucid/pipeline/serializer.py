"""
serializer.py
-------------
Converts the domain model objects (SalesItem, SalesCategory, SalesReport)
into plain Python dicts that are ready for JSON serialization.

Warnings fields are included only when non-empty, keeping the output
clean for well-formed data while still surfacing issues when they exist.

Public API
----------
sales_item_to_dict(item)         -> dict
sales_category_to_dict(category) -> dict
sales_report_to_dict(report)     -> dict
"""

from __future__ import annotations

from typing import Any, Dict

# from models import SalesCategory, SalesItem, SalesReport
from transormer.sales.lucid.pipeline.models import SalesCategory, SalesItem, SalesReport

def sales_item_to_dict(item: SalesItem) -> Dict[str, Any]:
    """
    Serialize a ``SalesItem`` to a plain dict.

    The ``warnings`` key is omitted when the list is empty.

    Parameters
    ----------
    item : SalesItem

    Returns
    -------
    dict
        Keys: product_name, quantity, unit_price, total_price, date, menu,
        and optionally warnings.
    """
    result: Dict[str, Any] = {
        "product_name": item.product_name,
        "quantity":     item.quantity,
        "unit_price":   item.unit_price,
        "total_price":  item.total_price,
        "date":         item.date,
        "menu":         item.menu,
    }
    if item.warnings:
        result["warnings"] = item.warnings
    return result


def sales_category_to_dict(category: SalesCategory) -> Dict[str, Any]:
    """
    Serialize a ``SalesCategory`` (and all its items) to a plain dict.

    Parameters
    ----------
    category : SalesCategory

    Returns
    -------
    dict
        Keys: category_name, total_category_sales, items,
        and optionally warnings.
    """
    result: Dict[str, Any] = {
        "category_name":        category.category_name,
        "total_category_sales": category.total_category_sales,
        "items": [sales_item_to_dict(item) for item in category.items],
    }
    if category.warnings:
        result["warnings"] = category.warnings
    return result


def sales_report_to_dict(report: SalesReport) -> Dict[str, Any]:
    """
    Serialize a complete ``SalesReport`` to a plain dict suitable for
    ``json.dumps`` or any downstream consumer.

    Parameters
    ----------
    report : SalesReport

    Returns
    -------
    dict
        Keys: date_range, restaurant, total_sales, categories,
        and optionally warnings.
    """
    result: Dict[str, Any] = {
        "date_range":  report.date_range,
        "restaurant":  report.restaurant,
        "total_sales": report.total_sales,
        "categories": [
            sales_category_to_dict(cat) for cat in report.categories
        ],
    }
    if report.warnings:
        result["warnings"] = report.warnings
    return result