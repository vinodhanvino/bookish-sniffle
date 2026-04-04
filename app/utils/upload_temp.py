"""Save an uploaded file to a temporary path for synchronous processing."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile


async def write_upload_to_temp(upload: UploadFile, suffix: str) -> tuple[Path, str]:
    """Returns (temp_path, original_filename). Caller must delete temp_path when done."""
    name = (upload.filename or "").lower()
    ext = Path(name).suffix or suffix
    with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        data = await upload.read()
        tmp.write(data)
        return Path(tmp.name), upload.filename or f"upload{suffix}"
