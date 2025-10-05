from fastapi import FastAPI

from app.api.documentos import router as documentos_router
import logging

logging.basicConfig(
    filename="app/logs/app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = FastAPI()

app.include_router(documentos_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Gestor Documental en marcha 🚀"}