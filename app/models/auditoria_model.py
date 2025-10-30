# app/models/auditoria_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class Auditoria(Base):
    __tablename__ = 'auditoria'

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(100), nullable=False)
    accion = Column(String(255), nullable=False)
    entidad = Column(String(100), nullable=False)
    detalle = Column(Text, nullable=True)
    fecha_hora = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Auditoria {self.usuario} - {self.accion}>'
