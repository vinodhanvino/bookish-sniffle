"""
models.py
---------
Pure data models (dataclasses) that represent every layer of the
sales report domain:  SalesItem → SalesCategory → SalesReport.

These classes carry no I/O or business logic — they are plain containers
that the rest of the library reads and writes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SalesItem:
    """
    A single sold product line (ItemType == 'I' in the source sheet).

    Attributes
    ----------
    product_name : str
        Display name of the product as it appears on the menu.
    quantity : float
        Number of units sold.
    unit_price : float
        Price per unit (rounded to 2 decimal places).
    total_price : float
        Recorded total from the source (quantity × unit_price, verified).
    date : str
        Sale date in ISO-8601 format (YYYY-MM-DD).
    menu : str
        Menu / sub-section the item belongs to (e.g. "Bar Tit Bits").
    warnings : list of str
        Non-empty when a data-quality issue was detected for this item
        (e.g. computed total differs from recorded total).
    """

    product_name: str
    quantity: float
    unit_price: float
    total_price: float
    date: str
    menu: str
    warnings: List[str] = field(default_factory=list)


@dataclass
class SalesCategory:
    """
    A classification group that aggregates one or more SalesItems.

    Examples of category names: 'Food', 'Liquor', 'Others', 'Tobacco'.

    Attributes
    ----------
    category_name : str
        Name of the classification (as found in the 'Classification' column).
    total_category_sales : float
        Sum of all item total_prices within this category.
    items : list of SalesItem
        All individual sale lines that belong to this category.
    warnings : list of str
        Non-empty when the sum of item totals does not match the
        category total recorded in the source file.
    """

    category_name: str
    total_category_sales: float
    items: List[SalesItem] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SalesReport:
    """
    Root object that represents a complete itemwise sales report.

    Attributes
    ----------
    date_range : str
        Reporting window expressed as 'YYYY-MM-DD/YYYY-MM-DD'.
    restaurant : str
        Name of the restaurant / outlet.
    total_sales : float
        Grand total of all sales across every category.
    categories : list of SalesCategory
        All category groups contained in the report.
    warnings : list of str
        Top-level warnings (e.g. category-sum mismatch, suspicious prices).
    """

    date_range: str
    restaurant: str
    total_sales: float
    categories: List[SalesCategory] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)