# app/models/historial_documento.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base
from datetime import datetime

class HistorialDocumento(Base):
    __tablename__ = "historial_documentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String, nullable=False)
    version = Column(String, nullable=True)
    usuario = Column(String, nullable=False)  # puedes mantener para mostrar
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  # nuevo
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    hash_md5 = Column(String, nullable=False)
