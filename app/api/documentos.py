from fastapi import APIRouter, UploadFile, File
from app.models.documento import UploadResponse
from app.services.document_service import procesar_documento
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Subiendo archivo: {file.filename}")
    resultado = procesar_documento(file)
    return UploadResponse(**resultado)
