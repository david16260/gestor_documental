from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.historial_documento import HistorialDocumento
from app.api.auth import get_current_user

router = APIRouter(prefix="/documentos/versiones", tags=["Versiones"])

# --- Dependencia DB ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Listar documentos y sus versiones ---
@router.get("/")
def listar_documentos_versiones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Devuelve todos los documentos con sus versiones del usuario logueado.
    Ejemplo de respuesta:
    {
        "documentos": [
            {"nombre": "Manual.pdf", "versiones": [...]},
            ...
        ]
    }
    """
    # 1️⃣ Obtener todos los registros del historial del usuario
    registros = (
        db.query(HistorialDocumento)
        .filter(HistorialDocumento.usuario_id == current_user.id)
        .order_by(HistorialDocumento.nombre_archivo, HistorialDocumento.version.desc())
        .all()
    )

    # 2️⃣ Agrupar por nombre_archivo
    documentos_dict = {}
    for r in registros:
        if r.nombre_archivo not in documentos_dict:
            documentos_dict[r.nombre_archivo] = []
        documentos_dict[r.nombre_archivo].append({
            "version": r.version,
            "fecha_subida": str(r.fecha_subida) if r.fecha_subida else None,
            "usuario": current_user.nombre,
        })

    # 3️⃣ Convertir a lista
    documentos = [
        {"nombre": nombre, "versiones": versiones}
        for nombre, versiones in documentos_dict.items()
    ]

    return {"documentos": documentos}
