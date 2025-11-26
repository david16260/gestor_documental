import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.documento import Documento
from app.utils.validaciones import tiene_firma_digital
from app.api.documentos import calcular_md5_contenido

router = APIRouter(prefix="/ingesta", tags=["Ingesta"])
settings = get_settings()


@router.post("/carpeta")
def ingestar_carpeta(
    ruta: str,
    version: str = "1.0",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    base = Path(ruta)
    if not base.exists() or not base.is_dir():
        raise HTTPException(status_code=400, detail="Ruta no válida")

    creados: List[int] = []
    for archivo in base.glob("**/*"):
        if archivo.is_dir():
            continue
        extension = archivo.suffix.lower()
        if extension not in settings.allowed_extensions:
            continue
        contenido = archivo.read_bytes()
        hash_md5 = calcular_md5_contenido(contenido)
        duplicado = (
            db.query(Documento)
            .filter(Documento.hash_archivo == hash_md5, Documento.usuario_id == current_user.id)
            .first()
        )
        if duplicado:
            continue

        doc = Documento(
            nombre_archivo=archivo.name,
            extension=extension,
            version=version,
            hash_archivo=hash_md5,
            ruta_guardado=str(archivo),
            tamano_kb=len(contenido) / 1024,
            duplicado=False,
            usuario_id=current_user.id,
        )
        if extension == ".pdf":
            doc.confianza_clasificacion = 0.5 if tiene_firma_digital(archivo) else 0.3
        db.add(doc)
        db.commit()
        db.refresh(doc)
        creados.append(doc.id)

    return {"ingresados": creados, "total": len(creados)}
