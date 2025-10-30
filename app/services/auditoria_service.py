# app/core/auditoria_service.py
from sqlalchemy.orm import Session
from app.core.auditoria_controller import registrar_auditoria

async def registrar_auditoria_async(
    db: Session,
    usuario: str,
    accion: str, 
    entidad: str,
    detalle: str = None
):
    """Registra una acción de auditoría de forma asíncrona."""
    return registrar_auditoria(db, usuario, accion, entidad, detalle)

# Función helper para usar en dependencias
def auditar_accion(accion: str, entidad: str, detalle: str = None):
    """Factory function para crear dependencias de auditoría."""
    def _auditar(db: Session, usuario: str = "sistema"):
        return registrar_auditoria(db, usuario, accion, entidad, detalle)
    return _auditar