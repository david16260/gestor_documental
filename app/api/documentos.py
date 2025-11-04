# app/api/documentos.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.documento import Documento
from app.models.historial_documento import HistorialDocumento
from app.utils.validaciones import validar_trd_ccd
from app.api.auth import get_current_user
import hashlib
import os
import magic
from PyPDF2 import PdfReader
import openpyxl
from datetime import datetime

router = APIRouter(tags=["Documentos"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".trd", ".ccd"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calcular_md5_contenido(contenido: bytes) -> str:
    return hashlib.md5(contenido).hexdigest()


# ===============================
# ENDPOINT: SUBIR DOCUMENTO
# ===============================
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    version: str = Form(...),
    categoria: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo '{extension}' no permitido")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx 10 MB)")

    # --- Carpeta por usuario ---
    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(exist_ok=True)

    file_path = user_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(contents)

    # Validaciones específicas de archivos
    if extension in {".trd", ".ccd"} and not validar_trd_ccd(file_path):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Archivo TRD/CCD inválido")

    try:
        if extension == ".pdf":
            PdfReader(str(file_path))
        elif extension == ".xlsx":
            openpyxl.load_workbook(str(file_path))
    except Exception:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Archivo corrupto o no procesable")

    # Calcular hash
    nuevo_hash = calcular_md5_contenido(contents)
    try:
        mime = magic.Magic(mime=True)
        tipo_archivo = mime.from_file(str(file_path))
    except Exception:
        tipo_archivo = "desconocido"

    # --- CHEQUEO DE DUPLICADOS SOLO DEL MISMO USUARIO ---
    duplicado = db.query(Documento).filter(
        Documento.hash_archivo == nuevo_hash,
        Documento.version == version,
        Documento.usuario_id == current_user.id
    ).first()
    if duplicado:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Ya subiste anteriormente el archivo '{file.filename}' con la versión '{version}'"
        )

    # --- Guardar en tabla documentos ---
    nuevo_doc = Documento(
        nombre_archivo=file.filename,
        extension=extension,
        version=version,
        hash_archivo=nuevo_hash,
        ruta_guardado=str(file_path),
        tamano_kb=len(contents) / 1024,
        duplicado=False,
        usuario_id=current_user.id,
        categoria=categoria,
        content_type=file.content_type,
        last_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(nuevo_doc)
    db.commit()
    db.refresh(nuevo_doc)

    # --- Guardar en tabla historial_documentos ---
    nuevo_historial = HistorialDocumento(
        nombre_archivo=file.filename,
        version=version,
        usuario=current_user.nombre,
        usuario_id=current_user.id,
        fecha_subida=datetime.now(),
        hash_md5=nuevo_hash
    )
    db.add(nuevo_historial)
    db.commit()

    return {
        "mensaje": f"Archivo '{file.filename}' cargado correctamente.",
        "documento_id": nuevo_doc.id,
        "hash_md5": nuevo_hash,
        "categoria": categoria,
        "tipo_archivo": tipo_archivo,
        "tamano_kb": round(nuevo_doc.tamano_kb, 2),
        "version": version,
        "usuario": current_user.nombre
    }


# ===============================
# ENDPOINT: HISTORIAL DE DOCUMENTOS POR USUARIO
# ===============================
@router.get("/historial")
def historial_documento(nombre_archivo: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Retorna todas las versiones existentes de un documento por nombre
    Solo para el usuario logueado.
    """
    resultados = db.query(HistorialDocumento).filter(
       HistorialDocumento.nombre_archivo.ilike(nombre_archivo),
    HistorialDocumento.usuario_id == current_user.id
).order_by(HistorialDocumento.fecha_subida).all()

    if not resultados:
        raise HTTPException(404, detail=f"No se encontraron versiones para '{nombre_archivo}'")

    historial = [
        {
            "version": r.version,
            "usuario": r.usuario,
            "fecha_subida": r.fecha_subida.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in resultados
    ]

    return {
        "nombre_archivo": nombre_archivo,
        "historial": historial
    }
