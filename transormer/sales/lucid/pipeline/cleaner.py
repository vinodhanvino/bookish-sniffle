"""
cleaner.py
----------
Stateless data-cleaning functions that transform the raw DataFrame
produced by ``reader.load_raw_excel`` into a tidy, analysis-ready form.

Each function has a single, well-defined responsibility and can be
composed in any order by the pipeline.

Public API
----------
filter_sale_items(df)          -> pd.DataFrame   (drop modifiers & summary rows)
coerce_numeric_columns(df)     -> pd.DataFrame   (safe numeric casting)
drop_incomplete_rows(df)       -> pd.DataFrame   (remove rows missing key fields)
round_currency_columns(df)     -> pd.DataFrame   (2 d.p. on all money fields)
standardize_string_columns(df) -> pd.DataFrame   (strip whitespace from text)
clean(df)                      -> pd.DataFrame   (runs all steps in order)
"""

from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# Column name constants (single source of truth)
# ---------------------------------------------------------------------------

COL_ITEM_NAME      = "ItemName"
COL_RATE           = "Rate"
COL_QTY            = "Qty"
COL_TOTAL_AMOUNT   = "TotalAmount"
COL_CLASSIFICATION = "Classification"
COL_RESTAURANT     = "RestaurantName"
COL_MENU           = "MenuName"
COL_CATEGORY       = "Category"
COL_ITEM_TYPE      = "ItemType"

_NUMERIC_COLUMNS   = [COL_RATE, COL_QTY, COL_TOTAL_AMOUNT]
_STRING_COLUMNS    = [COL_ITEM_NAME, COL_CLASSIFICATION, COL_RESTAURANT,
                      COL_MENU, COL_CATEGORY, COL_ITEM_TYPE]
_REQUIRED_COLUMNS  = [COL_ITEM_NAME, COL_RATE, COL_QTY, COL_TOTAL_AMOUNT]

# Only rows where ItemType == 'I' are actual sold items.
# Rows with ItemType == 'M' are order modifiers (e.g. "LESS CHILLY", "PARCEL").
_ITEM_TYPE_SALE     = "I"


# ---------------------------------------------------------------------------
# Individual cleaning steps
# ---------------------------------------------------------------------------

def filter_sale_items(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only rows that represent actual sold items (ItemType == 'I').

    Modifier rows (ItemType == 'M') are order-level notes attached to a
    parent item.  They carry no independent price or quantity and must be
    excluded before any aggregation.

    Summary / total rows (e.g. "Bar Tit Bits Total: 7") have NaN in the
    ItemType column and are also removed by this filter.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame straight from the Excel reader.

    Returns
    -------
    pd.DataFrame
        Subset containing only sold-item rows, with the original index reset.
    """
    mask = df[COL_ITEM_TYPE].astype(str).str.strip() == _ITEM_TYPE_SALE
    return df[mask].reset_index(drop=True)


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast Rate, Qty, and TotalAmount to float, setting unparseable values to NaN.

    This is non-destructive: rows with NaN are not removed here; that job
    belongs to ``drop_incomplete_rows``.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Copy with numeric columns safely cast to float64.
    """
    df = df.copy()
    for col in _NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def drop_incomplete_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove any rows that are missing a value in a required column.

    Required columns: ItemName, Rate, Qty, TotalAmount.
    A row is only meaningful for analysis if all four are present.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        DataFrame with incomplete rows removed and index reset.
    """
    return df.dropna(subset=_REQUIRED_COLUMNS).reset_index(drop=True)


def round_currency_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Round Rate and TotalAmount to 2 decimal places.

    Floating-point representation in the source (e.g. 249.9999999…
    stored as 250) is corrected to the nearest cent.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Copy with currency columns rounded.
    """
    df = df.copy()
    df[COL_RATE]         = df[COL_RATE].round(2)
    df[COL_TOTAL_AMOUNT] = df[COL_TOTAL_AMOUNT].round(2)
    return df


def standardize_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip leading/trailing whitespace from all text columns.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Copy with string columns stripped.
    """
    df = df.copy()
    for col in _STRING_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


# ---------------------------------------------------------------------------
# Composed pipeline entry-point
# ---------------------------------------------------------------------------

def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run all cleaning steps in the correct order and return a tidy DataFrame.

    Pipeline order
    --------------
    1. filter_sale_items       — drop modifiers and summary rows
    2. coerce_numeric_columns  — safe float casting
    3. drop_incomplete_rows    — remove rows missing key fields
    4. round_currency_columns  — fix floating-point representation
    5. standardize_string_columns — strip whitespace

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from ``reader.load_raw_excel``.

    Returns
    -------
    pd.DataFrame
        Fully cleaned, analysis-ready DataFrame.
    """
    df = filter_sale_items(df)
    df = coerce_numeric_columns(df)
    df = drop_incomplete_rows(df)
    df = round_currency_columns(df)
    df = standardize_string_columns(df)
    return df