# ============================================================
# 📁 app/api/documentos_versiones.py
# ============================================================
# Módulo encargado de gestionar las versiones de documentos,
# clasificación y reclasificación por parte del usuario autenticado.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException       # Herramientas de FastAPI
from sqlalchemy.orm import Session                         # Manejo de sesiones de base de datos
from app.database import SessionLocal                      # Configuración de conexión a BD
from app.models.historial_documento import HistorialDocumento  # Modelo del historial de versiones
from app.models.documento import Documento                  # Modelo de documento actual
from app.api.auth import get_current_user                   # Dependencia para obtener usuario logueado
from pydantic import BaseModel                              # Validación de datos de entrada

# ============================================================
# 🚀 Configuración del router principal
# ============================================================
# Prefijo: /documentos/versiones
# Etiqueta: "Versiones" (para Swagger)
router = APIRouter(prefix="/documentos/versiones", tags=["Versiones"])

# ============================================================
# 🧩 Dependencia para la sesión de base de datos
# ============================================================
def get_db():
    """Crea y cierra la sesión de base de datos para cada solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# 📋 Obtener versiones distintas del usuario autenticado
# ============================================================
@router.get("/")
def versiones_vigentes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Devuelve todas las versiones únicas de documentos
    asociadas al usuario actualmente autenticado.
    """
    resultados = (
        db.query(HistorialDocumento.version)
        .filter(HistorialDocumento.usuario_id == current_user.id)
        .distinct()
        .all()
    )

    # Extrae las versiones en una lista limpia
    versiones = [v[0] for v in resultados if v[0] is not None]

    return {"versiones": versiones}

# ============================================================
# 📂 Consultar documentos clasificados por categoría o confidencialidad
# ============================================================
@router.get("/clasificados")
def documentos_clasificados(
    categoria: str | None = None,                # Filtro opcional por categoría
    confidencialidad: str | None = None,         # Filtro opcional por nivel de confidencialidad
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Permite al usuario listar documentos filtrando por categoría
    y/o confidencialidad. Solo devuelve documentos del usuario autenticado.
    """
    # Base de la consulta: documentos del usuario actual
    query = db.query(Documento).filter(Documento.usuario_id == current_user.id)

    # Aplicar filtros dinámicos según los parámetros
    if categoria:
        query = query.filter(Documento.categoria.ilike(f"%{categoria}%"))
    if confidencialidad:
        query = query.filter(Documento.confidencialidad.ilike(f"%{confidencialidad}%"))

    resultados = query.all()

    # Si no hay resultados, se retorna un error HTTP 404
    if not resultados:
        raise HTTPException(404, detail="No se encontraron documentos con esos criterios")

    # Construcción de la respuesta con datos esenciales del documento
    return {
        "total": len(resultados),
        "documentos": [
            {
                "id": d.id,
                "nombre": d.nombre_archivo,
                "categoria": d.categoria,
                "confidencialidad": d.confidencialidad,
                "tipo_documento": d.tipo_documento,
                "autor": d.autor,
                "version": d.version
            }
            for d in resultados
        ]
    }

# ============================================================
# ✏️ Modelo Pydantic para reclasificación de documento
# ============================================================
class ReclasificacionRequest(BaseModel):
    """Estructura de los datos requeridos para reclasificar un documento."""
    categoria: str
    confidencialidad: str
    tipo_documento: str | None = None
    autor: str | None = None

# ============================================================
# 🔄 Endpoint para reclasificar un documento existente
# ============================================================
@router.put("/reclasificar/{documento_id}")
def reclasificar_documento(
    documento_id: int,
    datos: ReclasificacionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Permite al usuario actualizar los campos de clasificación del documento:
    - categoría
    - confidencialidad
    - tipo_documento (opcional)
    - autor (opcional)
    """
    # Buscar el documento y verificar que pertenezca al usuario logueado
    doc = db.query(Documento).filter(
        Documento.id == documento_id,
        Documento.usuario_id == current_user.id
    ).first()

    # Si no existe o no pertenece al usuario → error 404
    if not doc:
        raise HTTPException(404, detail="Documento no encontrado o no pertenece al usuario")

    # Actualizar los valores de clasificación
    doc.categoria = datos.categoria
    doc.confidencialidad = datos.confidencialidad
    if datos.tipo_documento is not None:
        doc.tipo_documento = datos.tipo_documento
    if datos.autor is not None:
        doc.autor = datos.autor

    # Guardar cambios en la base de datos
    db.commit()
    db.refresh(doc)

    # Retornar respuesta con datos actualizados
    return {
        "mensaje": "Documento reclasificado correctamente",
        "documento": {
            "id": doc.id,
            "nombre": doc.nombre_archivo,
            "categoria": doc.categoria,
            "confidencialidad": doc.confidencialidad,
            "tipo_documento": doc.tipo_documento,
            "autor": doc.autor
        }
    }
