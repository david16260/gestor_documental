import os
from pathlib import Path

# Directorio de carga de archivos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Configuración de tamaño máximo y tipos
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".txt"}

print("📋 Configuración cargada correctamente")
