from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentoUploadResponse(BaseModel):
    mensaje: str
    documento_id: int
    hash_md5: str
    categoria: str
    tipo_archivo: str
    tamano_kb: float
    version: str
    usuario: str
    clasificacion: dict


class HistorialItem(BaseModel):
    version: str
    usuario: str
    fecha_subida: str


class HistorialResponse(BaseModel):
    nombre_archivo: str
    historial: List[HistorialItem]


class IndiceEntrada(BaseModel):
    orden: int
    documento_id: int
    nombre_archivo: str
    tamano_kb: float
    pagina_inicio: int
    pagina_fin: int
    fecha: Optional[str]


class IndiceResponse(BaseModel):
    usuario_id: int
    total_documentos: int
    total_paginas: int
    indice: List[IndiceEntrada]


class TRDEntryOut(BaseModel):
    id: int
    nombre: str
    version: str
    tipo: str
    archivo_nombre: str
    metadata: Optional[dict]
    class Config:
        orm_mode = True


class ClasificacionOut(BaseModel):
    documento_id: int
    clasificacion: dict
    confianza: float


class ExpedienteOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str]
    estado: str
    usuario_id: int
    creado_en: datetime
    class Config:
        orm_mode = True
