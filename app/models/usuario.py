from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String(50), nullable=False, server_default="user")  # <-- campo de rol incluido
    fecha_creacion = Column(DateTime, server_default=func.now())
    creado_en = Column(DateTime, server_default=func.now())
    
    # Campos para recuperación de contraseña
    reset_token = Column(String(100), nullable=True)
    reset_token_exp = Column(DateTime, nullable=True)