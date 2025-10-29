# app/config.py

import os
from pathlib import Path

# -----------------------------
# Información general del proyecto
# -----------------------------
APP_NAME = "Gestor Documental"
APP_ENV = "development"
APP_DEBUG = True

# -----------------------------
# Rutas del sistema
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # /app
UPLOAD_DIR = BASE_DIR / "uploads"

# Crear carpeta si no existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------
# Base de datos PostgreSQL
# -----------------------------
DB_ENGINE = "postgresql"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "gestor_documental"
DB_USER = "postgres"
DB_PASSWORD = "12345"

DATABASE_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# -----------------------------
# Seguridad JWT
# -----------------------------
SECRET_KEY = "mi_clave_secreta_para_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
