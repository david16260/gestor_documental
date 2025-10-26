# app/models/documento.py
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, func
from app.database import Base

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String, nullable=False)
    extension = Column(String, nullable=False)
    version = Column(String, nullable=True)
    hash_archivo = Column(String, unique=True, nullable=False)
    ruta_guardado = Column(String, nullable=False)
    tamano_kb = Column(Float, nullable=False)
    duplicado = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime, server_default=func.now())
    # Metadatos extra
    content_type = Column(String, nullable=True)
    last_modified = Column(String, nullable=True)
    servidor = Column(String, nullable=True)