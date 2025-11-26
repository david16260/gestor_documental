from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON

from app.core.database import Base


class TRDEntry(Base):
    __tablename__ = "trd_entries"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False, default="1.0")
    tipo = Column(String(50), nullable=False, default="TRD")  # TRD o CCD
    archivo_nombre = Column(String(255), nullable=False)
    metadata = Column(JSON, nullable=True)
    descripcion = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
