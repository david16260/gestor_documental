# app/api/documentos_versiones.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.historial_documento import HistorialDocumento
from app.api.auth import get_current_user

router = APIRouter(prefix="/documentos/versiones", tags=["Versiones"])

# DEPENDENCIA DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# LISTAR VERSIONES DEL USUARIO LOGUEADO
@router.get("/")
def versiones_vigentes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Devuelve todas las versiones registradas de documentos en el historial
    SOLO del usuario logueado.
    URL: /documentos/versiones
    """
    resultados = (
        db.query(HistorialDocumento.version)
        .filter(HistorialDocumento.usuario_id == current_user.id)  # filtrar por ID
        .distinct()
        .all()
    )

    versiones = [v[0] for v in resultados if v[0] is not None]
    return {"versiones": versiones}
