from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # 🔹 Cambiado de password
    fecha_creacion = Column(DateTime, server_default=func.now())
    creado_en = Column(DateTime, server_default=func.now())
