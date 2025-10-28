# ============================================================
# 📁 app/api/documentos.py
# ============================================================
# Módulo que maneja la subida, validación, clasificación y
# versionado de documentos dentro del sistema.
# ============================================================

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

# ============================================================
# 🚀 Configuración del router
# ============================================================
router = APIRouter(tags=["Documentos"])

# ============================================================
# 📂 Directorio de subida y parámetros globales
# ============================================================
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Crea carpeta si no existe

# Tipos de archivos permitidos
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".trd", ".ccd"}

# Tamaño máximo (10 MB)
MAX_SIZE_BYTES = 10 * 1024 * 1024


# ============================================================
# 🧩 Dependencia: conexión a base de datos
# ============================================================
def get_db():
    """Crea una sesión de BD y la cierra al finalizar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 🔐 Función auxiliar: calcular hash MD5 de contenido
# ============================================================
def calcular_md5_contenido(contenido: bytes) -> str:
    """Devuelve el hash MD5 para detectar duplicados."""
    return hashlib.md5(contenido).hexdigest()


# ============================================================
# 📤 ENDPOINT: Subir un documento al servidor
# ============================================================
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    version: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Sube un archivo, valida su estructura, firma digital, metadatos,
    calcula su hash y lo registra tanto en `documentos` como en `historial_documento`.
    """

    # --- Verificar extensión permitida ---
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo '{extension}' no permitido")

    # --- Leer contenido completo del archivo ---
    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx 10 MB)")

    # --- Verificación de permisos del usuario ---
    if hasattr(current_user, "rol") and current_user.rol not in {"admin", "editor"}:
        raise HTTPException(status_code=403, detail="No tienes permisos para subir documentos")

    # --- Crear carpeta personalizada del usuario ---
    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(exist_ok=True)

    # --- Guardar archivo físico ---
    file_path = user_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(contents)

    # --- Validar estructura de TRD/CCD ---
    if extension in {".trd", ".ccd"} and not validar_trd_ccd(file_path):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Archivo TRD/CCD inválido")

    # --- Validar integridad básica (PDF o Excel) ---
    try:
        if extension == ".pdf":
            PdfReader(str(file_path))  # Si no se puede abrir, lanza error
        elif extension == ".xlsx":
            openpyxl.load_workbook(str(file_path))
    except Exception:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Archivo corrupto o no procesable")

    # --- Validar firma digital (solo PDF) ---
    from app.utils.validaciones import tiene_firma_digital
    if extension == ".pdf" and not tiene_firma_digital(file_path):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="El documento PDF no tiene firma digital válida")

    # ============================================================
    # 📄 Extracción de metadatos básicos
    # ============================================================
    autor = current_user.nombre  # Se toma del usuario autenticado
    fecha_subida = datetime.now()
    tipo_documento = None

    # Detectar tipo de documento según extensión
    if extension == ".pdf":
        try:
            reader = PdfReader(str(file_path))
            tipo_documento = "PDF"
            if not reader.metadata or not reader.metadata.get("/Author"):
                raise HTTPException(status_code=400, detail="El PDF no contiene metadatos de autor")
        except Exception:
            raise HTTPException(status_code=400, detail="No se pudo extraer metadatos del PDF")
    elif extension == ".docx":
        tipo_documento = "Word"
    elif extension == ".xlsx":
        tipo_documento = "Excel"
    elif extension in {".jpg", ".png"}:
        tipo_documento = "Imagen"
    else:
        tipo_documento = "Otro"

    # ============================================================
    # 🗂 Clasificación automática inicial
    # ============================================================
    categoria = "General"
    confidencialidad = "Media"

    if "factura" in file.filename.lower():
        categoria = "Finanzas > Facturas"
        confidencialidad = "Alta"
    elif "contrato" in file.filename.lower():
        categoria = "Legal > Contratos"
        confidencialidad = "Confidencial"
    elif extension in {".jpg", ".png"}:
        categoria = "Imágenes"

    # ============================================================
    # 🔑 Calcular hash y MIME
    # ============================================================
    nuevo_hash = calcular_md5_contenido(contents)
    try:
        mime = magic.Magic(mime=True)
        tipo_archivo = mime.from_file(str(file_path))
    except Exception:
        tipo_archivo = "desconocido"

    # ============================================================
    # 🧾 Comprobación de duplicado (por hash + versión + usuario)
    # ============================================================
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

    # ============================================================
    # 💾 Registrar documento principal en BD
    # ============================================================
    nuevo_doc = Documento(
        nombre_archivo=file.filename,
        extension=extension,
        version=version,
        hash_archivo=nuevo_hash,
        ruta_guardado=str(file_path),
        tamano_kb=len(contents) / 1024,
        duplicado=False,
        usuario_id=current_user.id,
        creado_en=fecha_subida,
        tipo_documento=tipo_documento,
        categoria=categoria,
        confidencialidad=confidencialidad,
        autor=autor
    )
    db.add(nuevo_doc)
    db.commit()
    db.refresh(nuevo_doc)

    # ============================================================
    # 🕓 Guardar entrada en historial de versiones
    # ============================================================
    nuevo_historial = HistorialDocumento(
        nombre_archivo=file.filename,
        version=version,
        usuario=current_user.nombre,
        usuario_id=current_user.id,
        fecha_subida=fecha_subida,
        hash_md5=nuevo_hash
    )
    db.add(nuevo_historial)
    db.commit()

    # ============================================================
    # ✅ Respuesta final con detalles del documento
    # ============================================================
    return {
        "mensaje": f"Archivo '{file.filename}' cargado correctamente.",
        "documento_id": nuevo_doc.id,
        "hash_md5": nuevo_hash,
        "tipo_archivo": tipo_archivo,
        "tamano_kb": round(nuevo_doc.tamano_kb, 2),
        "version": version,
        "usuario": current_user.nombre,
        "clasificacion": {
            "tipo_documento": tipo_documento,
            "categoria": categoria,
            "confidencialidad": confidencialidad,
            "autor": autor
        }
    }


# ============================================================
# 📜 ENDPOINT: Consultar historial de versiones
# ============================================================
@router.get("/historial")
def historial_documento(
    nombre_archivo: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Devuelve todas las versiones existentes de un documento
    específico subido por el usuario actual.
    """

    # Buscar historial por nombre y usuario
    resultados = db.query(HistorialDocumento).filter(
        HistorialDocumento.nombre_archivo.ilike(nombre_archivo),
        HistorialDocumento.usuario_id == current_user.id
    ).order_by(HistorialDocumento.fecha_subida).all()

    if not resultados:
        raise HTTPException(404, detail=f"No se encontraron versiones para '{nombre_archivo}'")

    # Convertir resultados a lista de dicts legibles
    historial = [
        {
            "version": r.version,
            "usuario": r.usuario,
            "fecha_subida": r.fecha_subida.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in resultados
    ]

    # Respuesta con todas las versiones
    return {
        "nombre_archivo": nombre_archivo,
        "historial": historial
    }
