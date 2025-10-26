from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.services.fuid_service import FUIDService
from app.api.auth import get_current_user

router = APIRouter()

# Crear dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_fuid(
    request_data: dict,  # ← Recibir todo como JSON
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Crear un nuevo FUID"""
    service = FUIDService(db)
    
    try:
        # Validar que venga el expediente_id
        expediente_id = request_data.get("expediente_id")
        if expediente_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="El campo 'expediente_id' es requerido"
            )
        
        fuid = service.create_fuid(
            expediente_id=expediente_id,
            usuario_id=current_user.id,
            metadatos_fuid=request_data.get("metadatos_fuid"),
            referencia_contenido=request_data.get("referencia_contenido")
        )
        
        return {
            "mensaje": "FUID creado exitosamente",
            "fuid": fuid.numero_fuid,
            "id": fuid.id,
            "hash": fuid.hash_fuid,
            "fecha_generacion": fuid.fecha_generacion.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error interno al crear FUID"
        )

@router.get("/")
def listar_fuids(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Listar FUIDs del usuario"""
    service = FUIDService(db)
    fuids = service.get_fuids_by_usuario(current_user.id, skip, limit)
    
    return [
        {
            "id": fuid.id,
            "numero_fuid": fuid.numero_fuid,
            "expediente_id": fuid.expediente_id,
            "fecha_generacion": fuid.fecha_generacion.isoformat(),
            "hash_fuid": fuid.hash_fuid,
            "referencia_contenido": fuid.referencia_contenido,
            "metadatos_fuid": fuid.metadatos_fuid
        }
        for fuid in fuids
    ]

@router.get("/{fuid_id}")
def obtener_fuid(
    fuid_id: int, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Obtener un FUID específico"""
    service = FUIDService(db)
    fuid = service.get_fuid_by_id(fuid_id, current_user.id)
    
    if not fuid:
        raise HTTPException(status_code=404, detail="FUID no encontrado")
    
    return {
        "id": fuid.id,
        "numero_fuid": fuid.numero_fuid,
        "expediente_id": fuid.expediente_id,
        "fecha_generacion": fuid.fecha_generacion.isoformat(),
        "metadatos_fuid": fuid.metadatos_fuid,
        "referencia_contenido": fuid.referencia_contenido,
        "hash_fuid": fuid.hash_fuid,
        "creado_en": fuid.creado_en.isoformat()
    }

@router.put("/{fuid_id}")
def actualizar_fuid(
    fuid_id: int,
    request_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Actualizar metadata de un FUID"""
    service = FUIDService(db)
    fuid = service.update_fuid(
        fuid_id, 
        current_user.id, 
        request_data.get("metadatos_fuid"),
        request_data.get("referencia_contenido")
    )
    
    if not fuid:
        raise HTTPException(status_code=404, detail="FUID no encontrado")
    
    return {
        "mensaje": "FUID actualizado exitosamente",
        "fuid": fuid.numero_fuid,
        "metadatos_fuid_actualizada": fuid.metadatos_fuid
    }

@router.delete("/{fuid_id}")
def eliminar_fuid(
    fuid_id: int, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Eliminar un FUID"""
    service = FUIDService(db)
    success = service.delete_fuid(fuid_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="FUID no encontrado")
    
    return {"message": "FUID eliminado exitosamente"}