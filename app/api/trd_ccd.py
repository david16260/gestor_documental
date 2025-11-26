from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.trd_ccd import TRDEntry
from app.schemas.core import TRDEntryOut
from app.utils.validaciones import validar_trd_ccd
from app.config import settings

router = APIRouter(prefix="/trd", tags=["TRD/CCD"])


@router.post("/upload")
async def cargar_trd_ccd(
    file: UploadFile = File(...),
    tipo: str = "TRD",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    extension = Path(file.filename).suffix.lower()
    if extension not in {".trd", ".ccd", ".zip"}:
        raise HTTPException(status_code=400, detail="Formato no soportado para TRD/CCD")

    contents = await file.read()
    temp_dir = settings.base_dir / "tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / file.filename
    temp_path.write_bytes(contents)

    try:
        if not validar_trd_ccd(temp_path):
            raise HTTPException(status_code=400, detail="Estructura TRD/CCD inválida")
    finally:
        if temp_path.exists():
            temp_path.unlink()

    entry = TRDEntry(
        nombre=file.filename,
        archivo_nombre=file.filename,
        tipo=tipo.upper(),
        version="1.0",
        metadata={"validado": True, "uploader": current_user.email},
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {"id": entry.id, "nombre": entry.nombre, "tipo": entry.tipo, "version": entry.version}


@router.get("/", response_model=list[TRDEntryOut])
def listar_trd_ccd(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    registros = db.query(TRDEntry).order_by(TRDEntry.creado_en.desc()).all()
    return registros
