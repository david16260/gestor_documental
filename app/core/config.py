import os
from pathlib import Path
from decouple import config

# Directorio de carga de archivos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Configuración de tamaño máximo y tipos
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = (".pdf", ".docx", ".xlsx", ".txt")

# Nueva configuración SGDEA APIs
class Settings:
    # Configuración de seguridad
    SECRET_KEY: str = config("SECRET_KEY", default="default-secret-key-change-in-production")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./gestor_documental.db")
    
    # Configuración SGDEA APIs
    PROJECT_NAME: str = "SGDEA - Gestor Documental"
    API_V1_STR: str = config("API_V1_STR", default="/api/v1")
    GRAPHQL_ENDPOINT: str = config("GRAPHQL_ENDPOINT", default="/graphql")
    EXPORT_FORMATS: list = config("EXPORT_FORMATS", default="json,xml").split(",")
    
    # Configuración de archivos (usando la configuración existente)
    UPLOAD_DIR: Path = UPLOAD_DIR
    MAX_FILE_SIZE: int = MAX_SIZE_BYTES
    ALLOWED_FILE_EXTENSIONS: tuple = ALLOWED_EXTENSIONS

# Instancia global de configuración
settings = Settings()

print("Configuration cargada correctamente")

