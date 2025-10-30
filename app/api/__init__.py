# app/api/__init__.py
# Este archivo puede estar vacío o contener solo:
from . import auth
from . import documentos
from . import documentos_versiones
from . import fuid
from . import documentos_url
from . import integration_router

__all__ = [
    "auth",
    "documentos", 
    "documentos_versiones",
    "fuid",
    "documentos_url", 
    "integration_router"
]