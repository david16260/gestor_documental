# app/main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import xml_router  # Nuevo import

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestor Documental con IA",
    description="Sistema de gestión documental - Sprint 1",
    version="1.0.0"
)

# Incluir routers existentes
# app.include_router(users_router.router)
# app.include_router(upload_router.router)

# Incluir nuevo router de XML
app.include_router(xml_router.router)

@app.get("/")
def read_root():
    return {
        "mensaje": "Gestor Documental con IA",
        "version": "1.0.0",
        "endpoints_disponibles": [
            "/docs - Documentación interactiva",
            "/xml/documento/{id} - Generar XML individual",
            "/xml/expediente/usuario/{id} - Generar XML expediente completo"
        ]
    }