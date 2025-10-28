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
        usuario_id=current_user.id
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
# ========== APIs SGDEA - GESTIÓN DOCUMENTAL ELECTRÓNICA ==========
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.schemas.sgdea import DocumentoSGDEA, DocumentoSGDEACreate, Expediente, ExpedienteCreate, Inventario, FormatoInventario
from app.services.document_service import DocumentoSGDEAService
from app.services.sgdea_services import ExpedienteService, InventarioService
from app.services.exportador_service import ExportadorService
from app.core.security import verificar_token

# Router para APIs SGDEA
sgdea_router = APIRouter()

# ========== ENDPOINTS PARA DOCUMENTOS SGDEA ==========
@sgdea_router.get("/sgdea/", response_model=List[DocumentoSGDEA])
async def listar_documentos_sgdea(
    skip: int = Query(0, ge=0, description="Número de elementos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de elementos"),
    expediente_id: Optional[str] = Query(None, description="Filtrar por expediente"),
    token: dict = Depends(verificar_token)
):
    """
    Obtener lista de documentos SGDEA con paginación y filtros.
    - **skip**: Número de documentos a saltar (para paginación)
    - **limit**: Número máximo de documentos a retornar
    - **expediente_id**: Filtrar documentos por ID de expediente
    """
    try:
        documentos = DocumentoSGDEAService.obtener_documentos_sgdea(skip, limit, expediente_id)
        return documentos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener documentos SGDEA: {str(e)}")

@sgdea_router.get("/sgdea/{documento_id}", response_model=DocumentoSGDEA)
async def obtener_documento_sgdea(
    documento_id: str,
    token: dict = Depends(verificar_token)
):
    """
    Obtener un documento SGDEA específico por su ID.
    """
    documento = DocumentoSGDEAService.obtener_documento_sgdea_por_id(documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento SGDEA no encontrado")
    return documento

@sgdea_router.post("/sgdea/", response_model=DocumentoSGDEA)
async def crear_documento_sgdea(
    documento: DocumentoSGDEACreate,
    token: dict = Depends(verificar_token)
):
    """
    Crear un nuevo documento SGDEA.
    - **titulo**: Título del documento (obligatorio)
    - **tipo_documento**: Tipo de documento (contrato, factura, reporte, etc.)
    - **contenido**: Contenido del documento
    - **expediente_id**: ID del expediente asociado (opcional)
    """
    try:
        nuevo_documento = DocumentoSGDEAService.crear_documento_sgdea(documento)
        return nuevo_documento
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear documento SGDEA: {str(e)}")

# ========== ENDPOINTS PARA EXPEDIENTES SGDEA ==========
@sgdea_router.get("/sgdea/expedientes/", response_model=List[Expediente])
async def listar_expedientes_sgdea(
    skip: int = Query(0, ge=0, description="Número de elementos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de elementos"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    token: dict = Depends(verificar_token)
):
    """
    Obtener lista de expedientes SGDEA con paginación y filtros.
    - **skip**: Número de expedientes a saltar (para paginación)
    - **limit**: Número máximo de expedientes a retornar
    - **estado**: Filtrar por estado (abierto, cerrado, archivado)
    """
    try:
        expedientes = ExpedienteService.obtener_expedientes(skip, limit, estado)
        return expedientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener expedientes: {str(e)}")

@sgdea_router.get("/sgdea/expedientes/{expediente_id}", response_model=Expediente)
async def obtener_expediente_sgdea(
    expediente_id: str,
    token: dict = Depends(verificar_token)
):
    """
    Obtener un expediente SGDEA específico por su ID.
    """
    expediente = ExpedienteService.obtener_por_id(expediente_id)
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    return expediente

@sgdea_router.post("/sgdea/expedientes/", response_model=Expediente)
async def crear_expediente_sgdea(
    expediente: ExpedienteCreate,
    token: dict = Depends(verificar_token)
):
    """
    Crear un nuevo expediente SGDEA.
    - **codigo**: Código único del expediente
    - **titulo**: Título del expediente
    - **clasificacion**: Clasificación del expediente
    """
    try:
        nuevo_expediente = ExpedienteService.crear_expediente(expediente)
        return nuevo_expediente
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear expediente: {str(e)}")

# ========== ENDPOINTS PARA INVENTARIOS SGDEA ==========
@sgdea_router.get("/sgdea/inventarios/", response_model=List[Inventario])
async def listar_inventarios_sgdea(
    token: dict = Depends(verificar_token)
):
    """
    Obtener lista de todos los inventarios SGDEA generados.
    """
    try:
        inventarios = InventarioService.obtener_inventarios()
        return inventarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener inventarios: {str(e)}")

@sgdea_router.post("/sgdea/inventarios/generar", response_model=Inventario)
async def generar_inventario_sgdea(
    nombre: str = Query(..., description="Nombre del inventario"),
    descripcion: str = Query("", description="Descripción del inventario"),
    formato: FormatoInventario = Query(FormatoInventario.JSON, description="Formato del inventario"),
    token: dict = Depends(verificar_token)
):
    """
    Generar un nuevo inventario SGDEA del sistema.
    - **nombre**: Nombre descriptivo del inventario
    - **descripcion**: Descripción opcional
    - **formato**: Formato de exportación (json, xml)
    """
    try:
        inventario = InventarioService.generar_inventario(nombre, descripcion, formato)
        return inventario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar inventario: {str(e)}")

@sgdea_router.get("/sgdea/inventarios/exportar/{inventario_id}")
async def exportar_inventario_sgdea(
    inventario_id: str,
    formato: FormatoInventario = Query(FormatoInventario.JSON, description="Formato de exportación"),
    token: dict = Depends(verificar_token)
):
    """
    Exportar un inventario SGDEA en formato JSON o XML.
    - **inventario_id**: ID del inventario a exportar
    - **formato**: Formato de exportación (json, xml)
    """
    try:
        inventario_data = {
            "id": inventario_id,
            "nombre": f"Inventario SGDEA {inventario_id}",
            "fecha_generacion": "2024-01-01T00:00:00",
            "elementos": [
                {"tipo": "expediente", "total": 10},
                {"tipo": "documento_sgdea", "total": 150}
            ],
            "total_elementos": 160
        }
        
        return ExportadorService.exportar_inventario(
            inventario_data, 
            formato, 
            f"inventario_sgdea_{inventario_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar inventario: {str(e)}")
