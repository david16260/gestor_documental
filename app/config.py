# app/config.py

# Configuración general
APP_NAME = "Gestor Documental"
APP_ENV = "development"
APP_DEBUG = True

# Base de datos PostgreSQL
DB_ENGINE = "postgresql"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "gestor_documental"
DB_USER = "postgres"
DB_PASSWORD = "12345"

# Cadena de conexión (SQLAlchemy)
DATABASE_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Seguridad JWT
SECRET_KEY = "mi_clave_secreta_para_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
