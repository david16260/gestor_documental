    from pydantic import BaseModel

    print("Cargando documento.py")

    class UploadResponse(BaseModel):
        filename: str
        size_kb: float
        duplicate: bool
        saved_path: str