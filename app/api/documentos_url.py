# app/api/documentos_url.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.documento import Documento
from app.services.documentos_url_service import process_external_document
from datetime import datetime
from email.utils import parsedate_to_datetime

router = APIRouter(tags=["Documentos desde URL"])


class URLRequest(BaseModel):
    url: HttpUrl
    version: str | None = "1.0"
    categoria: str | None = None


@router.post("/desde-url")
def desde_url(req: URLRequest, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    """
    Puede procesar:
    - Un archivo individual
    - Una carpeta completa de Drive (recursivo)
    """
    try:
        documentos_metadata = process_external_document(str(req.url), usuario.id, req.version)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not documentos_metadata:
        raise HTTPException(status_code=400, detail="No se obtuvo ningún archivo de la URL.")

    documentos_registrados = []

    for metadata in documentos_metadata:

        hash_val = metadata.get("hash_archivo")
        if not hash_val:
            continue

        existe = db.query(Documento).filter(Documento.hash_archivo == hash_val).first()
        duplicado = bool(existe)

        # Parse fecha HTTP
        last_modified_str = metadata.get("last_modified")
        if last_modified_str:
            try:
                creado_en = parsedate_to_datetime(last_modified_str)
            except:
                creado_en = datetime.utcnow()
        else:
            creado_en = datetime.utcnow()

        nuevo = Documento(
            nombre_archivo=metadata.get("nombre_archivo", "sin_nombre"),
            extension=metadata.get("extension", ""),
            version=metadata.get("version", "1.0"),
            hash_archivo=hash_val,
            ruta_guardado=metadata.get("ruta_guardado", ""),
            tamano_kb=float(metadata.get("tamano_kb", 0)),
            duplicado=duplicado,
            usuario_id=usuario.id,
            creado_en=creado_en,
            content_type=metadata.get("content_type"),
            last_modified=metadata.get("last_modified"),
            categoria=req.categoria,
            servidor=metadata.get("servidor")
        )

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)

        documentos_registrados.append({
            "id": nuevo.id,
            "nombre": nuevo.nombre_archivo,
            "extension": nuevo.extension,
            "version": nuevo.version,
            "ruta_guardado": nuevo.ruta_guardado,
            "tamano_kb": nuevo.tamano_kb,
            "duplicado": nuevo.duplicado,
            "categoria": nuevo.categoria
        })

    return {
        "status": "ok",
        "mensaje": f"{len(documentos_registrados)} documento(s) registrados",
        "documentos": documentos_registrados
    }
