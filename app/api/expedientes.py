from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.documento import Documento
from app.models.expediente import Expediente
from app.schemas.core import ExpedienteOut, IndiceResponse

router = APIRouter(prefix="/expedientes", tags=["Expedientes"])


@router.post("/", response_model=ExpedienteOut)
def crear_expediente(
    codigo: str,
    nombre: str,
    descripcion: str = "",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existente = db.query(Expediente).filter(Expediente.codigo == codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El expediente ya existe")

    exp = Expediente(
        codigo=codigo,
        nombre=nombre,
        descripcion=descripcion,
        usuario_id=current_user.id,
        estado="abierto",
        creado_en=datetime.utcnow(),
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.post("/{expediente_id}/agregar/{documento_id}")
def agregar_documento(
    expediente_id: int,
    documento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    exp = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    doc.expediente_id = exp.id
    db.commit()
    return {"mensaje": "Documento agregado al expediente", "expediente": exp.codigo}


@router.get("/{expediente_id}/indice", response_model=IndiceResponse)
def generar_indice_expediente(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    docs: List[Documento] = (
        db.query(Documento)
        .filter(Documento.expediente_id == expediente_id)
        .order_by(Documento.creado_en)
        .all()
    )
    if not docs:
        raise HTTPException(status_code=404, detail="No hay documentos en el expediente")

    indice = []
    pagina_actual = 1
    for idx, doc in enumerate(docs, start=1):
        num_paginas = max(1, int((doc.tamano_kb or 1) / 100))
        pagina_fin = pagina_actual + num_paginas - 1
        indice.append(
            {
                "orden": idx,
                "documento_id": doc.id,
                "nombre_archivo": doc.nombre_archivo,
                "pagina_inicio": pagina_actual,
                "pagina_fin": pagina_fin,
            }
        )
        pagina_actual = pagina_fin + 1

    return {"expediente_id": expediente_id, "total_paginas": pagina_actual - 1, "indice": indice, "usuario_id": current_user.id, "total_documentos": len(docs)}
