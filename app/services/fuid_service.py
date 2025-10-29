from sqlalchemy.orm import Session
from app.models.fuid import FUID
from app.utils.fuid_generator import generate_fuid
from app.utils.hash_generator import generate_hash
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FUIDService:
    def __init__(self, db: Session):
        self.db = db

    def create_fuid(self, expediente_id: int, usuario_id: int, metadatos_fuid: dict = None, referencia_contenido: str = None) -> FUID:
        try:
            # Generar número FUID único
            numero_fuid = generate_fuid()
            
            # Generar hash
            hash_data = {
                "expediente_id": expediente_id,
                "usuario_id": usuario_id,
                "metadatos_fuid": metadatos_fuid,  # ← Cambiado aquí
                "timestamp": str(datetime.now().timestamp())
            }
            hash_fuid = generate_hash(hash_data)
            
            db_fuid = FUID(
                numero_fuid=numero_fuid,
                expediente_id=expediente_id,
                usuario_id=usuario_id,
                metadatos_fuid=metadatos_fuid,  # ← Cambiado aquí
                referencia_contenido=referencia_contenido,
                hash_fuid=hash_fuid
            )
            
            self.db.add(db_fuid)
            self.db.commit()
            self.db.refresh(db_fuid)
            
            logger.info(f"FUID creado exitosamente: {db_fuid.numero_fuid}")
            return db_fuid
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear FUID: {str(e)}")
            raise

    def get_fuid_by_id(self, fuid_id: int, usuario_id: int = None) -> FUID:
        query = self.db.query(FUID).filter(FUID.id == fuid_id)
        if usuario_id:
            query = query.filter(FUID.usuario_id == usuario_id)
        return query.first()

    def get_fuid_by_numero(self, numero_fuid: str) -> FUID:
        return self.db.query(FUID).filter(FUID.numero_fuid == numero_fuid).first()

    def get_fuids_by_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(FUID).filter(
            FUID.usuario_id == usuario_id
        ).offset(skip).limit(limit).all()

    def update_fuid(self, fuid_id: int, usuario_id: int, metadatos_fuid: dict = None, referencia_contenido: str = None) -> FUID:
        db_fuid = self.get_fuid_by_id(fuid_id, usuario_id)
        if db_fuid:
            if metadatos_fuid is not None:  # ← Cambiado aquí
                db_fuid.metadatos_fuid = metadatos_fuid  # ← Cambiado aquí
            if referencia_contenido is not None:
                db_fuid.referencia_contenido = referencia_contenido
            self.db.commit()
            self.db.refresh(db_fuid)
        return db_fuid

    def delete_fuid(self, fuid_id: int, usuario_id: int) -> bool:
        db_fuid = self.get_fuid_by_id(fuid_id, usuario_id)
        if db_fuid:
            self.db.delete(db_fuid)
            self.db.commit()
            return True
        return False