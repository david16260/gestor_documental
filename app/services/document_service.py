from pathlib import Path
from app.core.config import UPLOAD_DIR

def listar_documentos():
    """Lista todos los documentos subidos."""
    return [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]

# ========== SERVICIOS SGDEA ==========
from app.schemas.sgdea import DocumentoSGDEA, DocumentoSGDEACreate
import uuid
from datetime import datetime

# Datos mock para SGDEA - luego integrar con BD real
documentos_sgdea_db = {}

class DocumentoSGDEAService:
    @staticmethod
    def obtener_documentos_sgdea(
        skip: int = 0, 
        limit: int = 100, 
        expediente_id: str = None
    ):
        """Obtener lista de documentos SGDEA con paginación y filtros"""
        documentos = list(documentos_sgdea_db.values())
        if expediente_id:
            documentos = [d for d in documentos if d.expediente_id == expediente_id]
        return documentos[skip:skip + limit]
    
    @staticmethod
    def obtener_documento_sgdea_por_id(documento_id: str):
        """Obtener un documento SGDEA por su ID"""
        return documentos_sgdea_db.get(documento_id)
    
    @staticmethod
    def crear_documento_sgdea(documento: DocumentoSGDEACreate):
        """Crear un nuevo documento SGDEA"""
        documento_id = str(uuid.uuid4())
        now = datetime.now()
        
        nuevo_documento = DocumentoSGDEA(
            id=documento_id,
            fecha_creacion=now,
            fecha_modificacion=now,
            **documento.dict()
        )
        documentos_sgdea_db[documento_id] = nuevo_documento
        return nuevo_documento
