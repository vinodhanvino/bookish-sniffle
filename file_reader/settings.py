"""File reader configuration."""

from pathlib import Path

# Default encoding for text-based files
DEFAULT_ENCODING = "utf-8"

# Pipeline paths (project root = parent of be/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
XLSX_SOURCE_DIR = _PROJECT_ROOT / "resource"
PROCESSED_OUTPUT_DIR = _PROJECT_ROOT / "resource" / "processed"
PROCESSED_JSON_FILENAME = "combined.json"

# Column names (first existing in row) used to extract qty from ML/MI in text
NAME_COLUMNS_FOR_QTY = ("s", "name", "Name", "product", "Product", "description", "Description")

# I/O buffer size (bytes) for faster reads on large files
FILE_READ_BUFFER_BYTES = 1024 * 1024  # 1 MiB

# Chunk size for read_chunked() when not specified
DEFAULT_CHUNK_SIZE = 50_000

# CSV defaults
CSV_DIALECT = "excel"
CSV_DELIMITER = ","
CSV_QUOTECHAR = '"'

# Excel defaults
EXCEL_SHEET_INDEX = 0
EXCEL_HEADER_ROW = 0

# Supported extensions per reader type
EXT_CSV = (".csv", ".tsv")
EXT_JSON = (".json", ".jsonl")
EXT_EXCEL = (".xlsx", ".xls")
EXT_XML = (".xml",)
EXT_YAML = (".yaml", ".yml")
EXT_TEXT = (".txt", ".log", ".md", ".ini", ".cfg", ".conf")
