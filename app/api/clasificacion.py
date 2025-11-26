from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.documento import Documento
from app.services.ia_classifier import etiquetar_documento
from app.schemas.core import ClasificacionOut

router = APIRouter(prefix="/clasificacion", tags=["Clasificación IA"])


@router.post("/{documento_id}", response_model=ClasificacionOut)
def clasificar_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    resultado = etiquetar_documento(doc)
    doc.serie = resultado["clasificacion"]["serie"]
    doc.subserie = resultado["clasificacion"]["subserie"]
    doc.categoria = resultado["clasificacion"]["categoria"]
    doc.confianza_clasificacion = resultado["confianza"]
    db.commit()

    return resultado


@router.get("/pendientes")
def documentos_pendientes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    docs = (
        db.query(Documento)
        .filter((Documento.confianza_clasificacion == None) | (Documento.confianza_clasificacion < 0.5))
        .all()
    )
    return {"pendientes": [d.id for d in docs]}
