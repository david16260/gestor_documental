# app/api/documentos_versiones.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.documento import Documento

router = APIRouter(prefix="/versiones", tags=["Versiones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def versiones_vigentes(db: Session = Depends(get_db)):
    """
    Devuelve todas las versiones registradas de documentos.
    """
    versiones = db.query(Documento.version).distinct().all()
    return {"versiones": [v[0] for v in versiones if v[0] is not None]}
