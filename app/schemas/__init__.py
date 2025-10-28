# app/schemas/__init__.py
# Esquemas Pydantic para las APIs del sistema

from .sgdea import (
    DocumentoSGDEA, DocumentoSGDEACreate, TipoDocumento, EstadoDocumento,
    Expediente, ExpedienteCreate, EstadoExpediente,
    Inventario, InventarioCreate, FormatoInventario
)

__all__ = [
    "DocumentoSGDEA", "DocumentoSGDEACreate", "TipoDocumento", "EstadoDocumento",
    "Expediente", "ExpedienteCreate", "EstadoExpediente",
    "Inventario", "InventarioCreate", "FormatoInventario"
]