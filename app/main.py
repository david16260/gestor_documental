# main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.api import auth       
from app.api import documentos  

# Crear todas las tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(title="Gestor Documental")

# Registrar routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(documentos.router, prefix="/documentos")

# Endpoint raíz
@app.get("/")
def root():
    return {"message": "Bienvenido al Gestor Documental API"}
