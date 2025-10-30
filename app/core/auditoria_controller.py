# app/core/auditoria_controller.py
from sqlalchemy.orm import Session
from app.models.auditoria_model import Auditoria

def registrar_auditoria(db: Session, usuario: str, accion: str, entidad: str, detalle: str = None):
    """Guarda un registro de auditoría en la base de datos."""
    nuevo_registro = Auditoria(
        usuario=usuario,
        accion=accion,
        entidad=entidad,
        detalle=detalle
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro

def obtener_auditoria(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve los registros de auditoría más recientes."""
    return db.query(Auditoria).order_by(Auditoria.fecha_hora.desc()).offset(skip).limit(limit).all()
