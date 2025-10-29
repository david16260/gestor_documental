from app.models.auditoria_model import Auditoria
from database import db

def registrar_auditoria(usuario, accion, entidad, detalle=None):
    """Guarda un registro de auditoría en la base de datos."""
    nuevo_registro = Auditoria(
        usuario=usuario,
        accion=accion,
        entidad=entidad,
        detalle=detalle
    )
    db.session.add(nuevo_registro)
    db.session.commit()

def obtener_auditoria():
    """Devuelve los registros de auditoría más recientes."""
    return Auditoria.query.order_by(Auditoria.fecha_hora.desc()).all()
