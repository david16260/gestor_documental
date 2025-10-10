from pathlib import Path
from app.core.config import UPLOAD_DIR

def listar_documentos():
    """Lista todos los documentos subidos."""
    return [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
