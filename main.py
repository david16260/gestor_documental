from fastapi import FastAPI

from app.api.documentos import router as documentos_router

app = FastAPI()

app.include_router(documentos_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Gestor Documental en marcha 🚀"}