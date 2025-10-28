# app/services/__init__.py
# Servicios de lógica de negocio

# Importar servicios SGDEA
from .sgdea_services import ExpedienteService, InventarioService

__all__ = [
    "ExpedienteService", 
    "InventarioService"
]