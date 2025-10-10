from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de conexión a PostgreSQL
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/gestor_documental"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para inyección de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
