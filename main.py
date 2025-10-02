from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
import hashlib

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Gestor Documental en marcha 🚀"}

# Carpeta donde se guardan los archivos
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xml", ".txt"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

class UploadResponse(BaseModel):
    filename: str
    size_kb: float
    duplicate: bool
    saved_path: str

def file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")

    contents = await file.read()
    size = len(contents)
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx 10MB)")

    hash_value = file_hash(contents)
    hash_path = UPLOAD_DIR / f"{hash_value}{ext}"
    duplicate = hash_path.exists()

    if not duplicate:
        with open(hash_path, "wb") as f:
            f.write(contents)

    return UploadResponse(
        filename=file.filename,
        size_kb=round(size / 1024, 2),
        duplicate=duplicate,
        saved_path=str(hash_path)
    )
