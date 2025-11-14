# app/api/documentos_url.py
from fastapi import APIRouter, Depends, HTTPException, status
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
def desde_url(req: URLRequest, db: Session = Depends(get_db), usuario = Depends(get_current_user)):
    """
    Recibe una URL pública (Drive/OneDrive/directa), descarga el archivo,
    extrae metadatos y lo registra en la tabla 'documentos'.
    """
    try:
        metadata = process_external_document(str(req.url),usuario.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la URL: {str(e)}")

    # Verificar duplicado por hash 
    hash_val = metadata.get("hash_archivo")
    if not hash_val:
        raise HTTPException(status_code=500, detail="No se pudo calcular el hash del archivo")

    existe = db.query(Documento).filter(Documento.hash_archivo == hash_val).first()
    duplicado = bool(existe)

        # Convertir last_modified HTTP a datetime
    last_modified_str = metadata.get("last_modified")
    if last_modified_str:
        try:
            creado_en = parsedate_to_datetime(last_modified_str)
        except Exception:
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

    # Preparar respuesta rica con metadatos extra
    response = {
        "status": "ok",
        "mensaje": "Documento registrado",
        "documento": {
            "id": nuevo.id,
            "nombre": nuevo.nombre_archivo,
            "extension": nuevo.extension,
            "version": nuevo.version,
            "tamano_kb": nuevo.tamano_kb,
            "ruta_guardado": nuevo.ruta_guardado,
            "duplicado": nuevo.duplicado,
            "creado_en": nuevo.creado_en.isoformat() if nuevo.creado_en else None,
            "categoria": nuevo.categoria
        },
        "metadatos_extra": {k: v for k, v in metadata.items() if k not in ("nombre_archivo", "extension", "version", "hash_archivo", "ruta_guardado", "tamano_kb")}
    }

    return response
