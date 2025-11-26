# app/models/documento.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from app.core.database import Base
from sqlalchemy.sql import func

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
    expediente_id = Column(Integer, ForeignKey("expedientes.id"), nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
    # Metadatos extra
    content_type = Column(String, nullable=True)
    last_modified = Column(String, nullable=True)
    servidor = Column(String, nullable=True)
    categoria = Column(String, nullable=True) 
    # Nuevos campos para FUID
    area = Column(String(100))
    serie = Column(String(100))
    subserie = Column(String(100))
    codigo_clasificacion = Column(String(50))
    nombre_unidad_documental = Column(String(255))
    confianza_clasificacion = Column(Float, default=0.0)
    palabras_clave_contextuales = Column(Text)
