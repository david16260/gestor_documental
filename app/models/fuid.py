from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from app.database import Base


class FUID(Base):
    __tablename__ = "fuids"

    id = Column(Integer, primary_key=True, index=True)
    numero_fuid = Column(String(200), unique=True, nullable=False)  # valor del FUID generado
    expediente_id = Column(Integer, nullable=False)  # referencia al expediente (si existe tabla de expedientes)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_generacion = Column(DateTime, server_default=func.now(), nullable=False)
    metadatos_fuid = Column(SQLiteJSON, nullable=True)  # información estructurada sobre el inventario
    referencia_contenido = Column(String, nullable=True)  # ruta o referencia al archivo FUID generado
    hash_fuid = Column(String, nullable=True, unique=True)
    creado_en = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<FUID id={self.id} numero_fuid={self.numero_fuid} expediente_id={self.expediente_id}>"
