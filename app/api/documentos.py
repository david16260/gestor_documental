# ============================================================
# 📁 app/api/documentos.py
# ============================================================
# Módulo que maneja la subida, validación, clasificación y
# versionado de documentos dentro del sistema.
# ============================================================

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Query
from fastapi.responses import StreamingResponse
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
from typing import List, Optional
import io
import csv
import math

# ============================================================
# 🚀 Configuración del router
# ============================================================
router = APIRouter(tags=["Documentos"])

# ========== APIs SGDEA - GESTIÓN DOCUMENTAL ELECTRÓNICA ==========
from app.schemas.sgdea import DocumentoSGDEA, DocumentoSGDEACreate, Expediente, ExpedienteCreate, Inventario, FormatoInventario
from app.services.document_service import DocumentoSGDEAService
from app.services.sgdea_services import ExpedienteService, InventarioService
from app.services.exportador_service import ExportadorService
from app.core.security import verificar_token

# Router para APIs SGDEA
sgdea_router = APIRouter()

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


# ============================================================
# 📇 ENDPOINT: Generar índice foliado para el usuario autenticado
# ============================================================
@router.get("/indice_foliado")
def generar_indice_foliado(
    formato: str = Query("json", description="Formato de salida: json o csv"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Genera un índice foliado para todos los documentos del usuario autenticado.
    Devuelve una lista con el orden, nombre de archivo, tamaño y páginas inicio/fin.
    Parámetros:
    - formato: 'json' (por defecto) o 'csv'
    """
    try:
        # Obtener documentos del usuario ordenados por fecha de creación
        documentos = db.query(Documento).filter(Documento.usuario_id == current_user.id).order_by(Documento.creado_en).all()

        if not documentos:
            raise HTTPException(status_code=404, detail="No se encontraron documentos para el usuario")

        indice = []
        pagina_actual = 1

        for idx, doc in enumerate(documentos, start=1):
            # Calcular páginas estimadas usando la misma heurística que el xml generator
            num_paginas = max(1, int(doc.tamano_kb / 100))
            pagina_fin = pagina_actual + num_paginas - 1

            indice.append({
                "orden": idx,
                "documento_id": doc.id,
                "nombre_archivo": doc.nombre_archivo,
                "tamano_kb": round(float(doc.tamano_kb), 2),
                "pagina_inicio": pagina_actual,
                "pagina_fin": pagina_fin,
                "fecha": doc.creado_en.strftime("%Y-%m-%d %H:%M:%S") if doc.creado_en else None
            })

            pagina_actual = pagina_fin + 1

        # Si el cliente solicitó CSV, construir respuesta streaming
        if formato.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["orden", "documento_id", "nombre_archivo", "tamano_kb", "pagina_inicio", "pagina_fin", "fecha"])
            for fila in indice:
                writer.writerow([
                    fila["orden"], fila["documento_id"], fila["nombre_archivo"], fila["tamano_kb"], fila["pagina_inicio"], fila["pagina_fin"], fila["fecha"]
                ])
            output.seek(0)
            headers = {
                "Content-Disposition": f"attachment; filename=indice_foliado_user_{current_user.id}.csv"
            }
            return StreamingResponse(output, media_type="text/csv", headers=headers)

        # Por defecto devolver JSON con índice y total de páginas
        total_paginas = pagina_actual - 1
        return {"usuario_id": current_user.id, "total_documentos": len(documentos), "total_paginas": total_paginas, "indice": indice}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar índice foliado: {str(e)}")