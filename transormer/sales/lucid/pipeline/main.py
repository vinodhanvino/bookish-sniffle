"""
main.py
-------
Command-line entry point for the sales ETL pipeline.

Usage
-----
    python main.py <input_xlsx> [output_json]

Arguments
---------
input_xlsx   Path to the source Excel sales report (.xlsx).
output_json  Optional path for the output JSON file.
             Defaults to the same directory as input_xlsx with a .json extension.

Examples
--------
    python main.py sales.xlsx
    python main.py sales.xlsx output/sales_report.json
"""

import argparse
import json
import sys
from pathlib import Path

from pipeline import run_etl


def main() -> None:
    run_etl(
        rf"D:\office\code\spirix\sales.xlsx",
        rf"D:\office\code\spirix\sales.json"
    )

if __name__ == "__main__":
    main()
