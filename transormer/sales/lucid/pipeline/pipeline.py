"""
pipeline.py
-----------
Orchestrates the full ETL pipeline by composing the reader, cleaner,
transformer, and serializer modules in a single callable flow.

                ┌──────────┐
    .xlsx  ───► │  reader  │  load_raw_excel + extract_report_metadata
                └────┬─────┘
                     │  raw DataFrame + metadata dict
                ┌────▼─────┐
                │  cleaner │  filter → coerce → drop → round → strip
                └────┬─────┘
                     │  clean DataFrame
                ┌────▼───────────┐
                │  transformer   │  DataFrame → SalesReport domain object
                └────┬───────────┘
                     │  SalesReport
                ┌────▼──────────┐
                │  serializer   │  SalesReport → dict  (JSON-ready)
                └────┬──────────┘
                     │
                  JSON file  /  dict

Public API
----------
run_etl(input_filepath, output_filepath=None)  -> dict
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from transormer.sales.lucid.pipeline import cleaner, reader, serializer, transformer
from transormer.sales.lucid.pipeline.models import SalesReport


def run_etl(
        input_filepath: str | Path,
        output_filepath: Optional[str | Path] = None,
) -> Dict:
    """
    Execute the complete Extract → Transform → Load pipeline.

    Steps
    -----
    1. **Extract**   – Read the raw Excel file and parse report metadata.
    2. **Clean**     – Filter, coerce, deduplicate, and normalise the data.
    3. **Transform** – Build the ``SalesReport`` domain object with inline
                       validation warnings.
    4. **Serialize** – Convert to a JSON-serializable dict.
    5. **Load**      – Optionally write the dict to a ``.json`` file.

    Parameters
    ----------
    input_filepath : str or Path
        Path to the source ``.xlsx`` sales report file.
    output_filepath : str or Path, optional
        Destination path for the output JSON file.
        When ``None``, no file is written (the dict is still returned).

    Returns
    -------
    dict
        JSON-serializable sales report dictionary.

    Examples
    --------
     from sales_etl.pipeline import run_etl
    result = run_etl("sales.xlsx", "sales.json")
    print(result["total_sales"])
    291850.39
    """
    # ── 1. Extract ────────────────────────────────────────────────────────
    raw_df = reader.load_raw_excel(input_filepath)
    metadata = reader.extract_report_metadata(input_filepath)

    # ── 2. Clean ──────────────────────────────────────────────────────────
    clean_df = cleaner.clean(raw_df)

    # ── 3. Transform ──────────────────────────────────────────────────────
    report: SalesReport = transformer.build_sales_report(clean_df, metadata)

    # ── 4. Serialize ──────────────────────────────────────────────────────
    report_dict = serializer.sales_report_to_dict(report)

    # ── 5. Load (optional) ────────────────────────────────────────────────
    if output_filepath is not None:
        _write_json(report_dict, Path(output_filepath))

    return report_dict


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _write_json(data: Dict, filepath: Path) -> None:
    """
    Serialise ``data`` to a formatted JSON file at ``filepath``.

    Creates parent directories automatically if they do not exist.

    Parameters
    ----------
    data : dict
    filepath : Path
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print(f"[pipeline] JSON written → {filepath}")
