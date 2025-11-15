# app/schemas/sgdea.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TipoDocumento(str, Enum):
    CONTRATO = "contrato"
    FACTURA = "factura"
    REPORTE = "reporte"
    OFICIO = "oficio"
    MEMORANDUM = "memorandum"
    OTRO = "otro"

class EstadoDocumento(str, Enum):
    BORRADOR = "borrador"
    REVISION = "revision"
    APROBADO = "aprobado"
    ARCHIVADO = "archivado"

class EstadoExpediente(str, Enum):
    ABIERTO = "abierto"
    CERRADO = "cerrado"
    ARCHIVADO = "archivado"

class FormatoInventario(str, Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"

class DocumentoSGDEABase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=500)
    tipo_documento: TipoDocumento
    contenido: str
    expediente_id: Optional[str] = None
    metadatos: dict = Field(default_factory=dict)

class DocumentoSGDEACreate(DocumentoSGDEABase):
    pass

class DocumentoSGDEA(DocumentoSGDEABase):
    id: str
    fecha_creacion: datetime
    fecha_modificacion: datetime
    estado: EstadoDocumento = EstadoDocumento.BORRADOR

    class Config:
        from_attributes = True

class ExpedienteBase(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=500)
    clasificacion: str = Field(..., min_length=1, max_length=100)

class ExpedienteCreate(ExpedienteBase):
    pass

class Expediente(ExpedienteBase):
    id: str
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime] = None
    estado: EstadoExpediente = EstadoExpediente.ABIERTO
    documentos: List[DocumentoSGDEA] = []

    class Config:
        from_attributes = True

class InventarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=500)

class InventarioCreate(InventarioBase):
    formato: FormatoInventario = FormatoInventario.JSON

class Inventario(InventarioBase):
    id: str
    fecha_generacion: datetime
    elementos: List[dict] = Field(default_factory=list)
    total_elementos: int = 0
    formato: FormatoInventario = FormatoInventario.JSON

    class Config:
        from_attributes = True