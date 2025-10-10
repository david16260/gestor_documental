# app/api/documentos.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.documento import Documento
from app.utils.validaciones import validar_trd_ccd
import hashlib
import os
import magic

router = APIRouter(tags=["Documentos"])

# Configuración
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
    """Calcula hash MD5 del contenido del archivo."""
    return hashlib.md5(contenido).hexdigest()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    usuario_id: int = 1,
    version: str = None,
    db: Session = Depends(get_db)
):
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo '{extension}' no permitido")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx 10 MB)")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(contents)

    # HU1: Validar TRD/CCD
    if extension in {".trd", ".ccd"} and not validar_trd_ccd(file_path):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Archivo TRD/CCD inválido según estructura")

    # HU5: Verificar archivos corruptos
    try:
        if extension == ".pdf":
            from PyPDF2 import PdfReader
            PdfReader(str(file_path))
        elif extension == ".xlsx":
            import openpyxl
            openpyxl.load_workbook(str(file_path))
    except Exception:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Archivo corrupto o no procesable")

    # HU4: Calcular hash y tipo MIME
    nuevo_hash = calcular_md5_contenido(contents)
    tipo_archivo = magic.from_file(str(file_path), mime=True)

    # HU5: Evitar duplicados **con misma versión**
    duplicado = db.query(Documento).filter(
        Documento.hash_archivo == nuevo_hash,
        Documento.version == version
    ).first()
    if duplicado:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"El archivo ya fue cargado anteriormente con la versión '{version}'"
        )

    # Guardar registro en BD
    nuevo_doc = Documento(
        nombre_archivo=file.filename,
        extension=extension,
        version=version,
        hash_archivo=nuevo_hash,
        ruta_guardado=str(file_path),
        tamano_kb=len(contents)/1024,
        duplicado=False,
        usuario_id=usuario_id
    )
    db.add(nuevo_doc)
    db.commit()
    db.refresh(nuevo_doc)

    return {
        "mensaje": f"Archivo '{file.filename}' cargado correctamente.",
        "documento_id": nuevo_doc.id,
        "hash_md5": nuevo_hash,
        "tipo_archivo": tipo_archivo,
        "tamano_kb": nuevo_doc.tamano_kb,
        "version": nuevo_doc.version
    }


# HU2: Consultar versiones vigentes
@router.get("/versiones")
def versiones_vigentes(db: Session = Depends(get_db)):
    versiones = db.query(Documento.version).distinct().all()
    return {"versiones": [v[0] for v in versiones if v[0] is not None]}

# HU6: Historial de versiones por archivo
@router.get("/historial")
def historial_documento(nombre_archivo: str, db: Session = Depends(get_db)):
    """
    Retorna todas las versiones existentes de un documento por nombre.
    """
    resultados = db.query(Documento.version).filter(Documento.nombre_archivo == nombre_archivo).order_by(Documento.version).all()
    versiones = [v[0] for v in resultados if v[0] is not None]
    
    if not versiones:
        raise HTTPException(status_code=404, detail=f"No se encontraron versiones para '{nombre_archivo}'")
    
    return {
        "nombre_archivo": nombre_archivo,
        "versiones": versiones
    }
