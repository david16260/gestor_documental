# app/models/fuid_models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from app.core.database import Base
from datetime import datetime
from sqlalchemy.sql import func

class FUID(Base):
    __tablename__ = "fuids"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_fuid = Column(String(200), unique=True, nullable=False)
    expediente_id = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_generacion = Column(DateTime, server_default=func.now(), nullable=False)
    metadatos_fuid = Column(SQLiteJSON, nullable=True)
    referencia_contenido = Column(String, nullable=True)
    hash_fuid = Column(String, nullable=True, unique=True)
    creado_en = Column(DateTime, server_default=func.now())


class ExpedienteFUID(Base):
    __tablename__ = "expedientes_fuid"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=False)
    nombre_series = Column(String(100), nullable=False)
    nombre_subseries = Column(String(100), nullable=True)
    nombre_unidad_documental = Column(String(255), nullable=False)
    fecha_inicial = Column(DateTime, nullable=False)
    fecha_final = Column(DateTime, nullable=False)
    electronico = Column(Boolean, default=True)
    ubicacion = Column(String(500), nullable=False)
    cantidad_documentos = Column(Integer, default=0)
    tamaño_documentos = Column(String(50), default="0MB")
    usuario_id = Column(Integer, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
