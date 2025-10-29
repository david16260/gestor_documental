from datetime import datetime
from app import db

class Auditoria(db.Model):
    __tablename__ = 'auditoria'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), nullable=False)
    accion = db.Column(db.String(255), nullable=False)
    entidad = db.Column(db.String(100), nullable=False)
    detalle = db.Column(db.Text, nullable=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Auditoria {self.usuario} - {self.accion}>'
