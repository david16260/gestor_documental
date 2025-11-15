from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.auditoria_controller import obtener_auditoria, registrar_auditoria
from app.database import get_db
from app.models.auditoria_model import Auditoria
# Si tienes autenticación, descomenta la siguiente línea:
# from app.core.security import require_role

router = APIRouter()

@router.get("/auditoria", response_model=List[dict])
def listar_auditoria(
    skip: int = Query(0, description="Número de registros a saltar"),
    limit: int = Query(100, description="Límite de registros a devolver"),
    db: Session = Depends(get_db),
    # Descomenta si quieres requerir autenticación:
    # current_user = Depends(require_role("admin", "auditor"))
):
    """Lista todos los registros de auditoría."""
    try:
        registros = obtener_auditoria(db, skip=skip, limit=limit)
        
        data = [
            {
                'id': r.id,
                'usuario': r.usuario,
                'accion': r.accion,
                'entidad': r.entidad,
                'detalle': r.detalle,
                'fecha_hora': r.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
            }
            for r in registros
        ]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener registros de auditoría: {str(e)}")

# Endpoint para crear registros de auditoría (testing)
@router.post("/auditoria")
def crear_registro_auditoria(
    usuario: str,
    accion: str,
    entidad: str,
    detalle: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Endpoint para crear registros de auditoría (para testing)."""
    try:
        registro = registrar_auditoria(db, usuario, accion, entidad, detalle)
        return {
            "message": "Registro de auditoría creado",
            "id": registro.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear registro de auditoría: {str(e)}")