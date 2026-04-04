from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.sales_upload_service import ingest_sales_file

router = APIRouter(prefix="/sales", tags=["sales-upload"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_sales_file(file: UploadFile = File(...)) -> dict:
    name = (file.filename or "").lower()
    if not name.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .xlsx files are supported for sales upload.",
        )

    suffix = Path(name).suffix or ".xlsx"
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        data = await file.read()
        tmp.write(data)
        temp_path = Path(tmp.name)

    try:
        return ingest_sales_file(temp_path, file.filename or "sales.xlsx")
    finally:
        temp_path.unlink(missing_ok=True)
