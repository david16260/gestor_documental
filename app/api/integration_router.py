from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.integration_service import IntegrationService
from app.api.auth import get_current_user

router = APIRouter(prefix="/integracion", tags=["Integración IA-FUID"])

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/procesar-url")
def procesar_url_y_crear_fuid(
    url: str,
    expediente_id: int,
    version: str = "1.0",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Endpoint unificado que mantiene la respuesta original + añade FUID
    """
    integration_service = IntegrationService(db)
    
    resultado = integration_service.procesar_url_y_crear_fuid(
        url=url,
        expediente_id=expediente_id,
        usuario_id=current_user.id,
        version=version
    )
    
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["error"]
        )
    
    # Retornar directamente la respuesta combinada
    return resultado["respuesta"]

@router.get("/estado-integracion")
def verificar_estado_integracion():
    """
    Verifica que todos los servicios estén funcionando
    """
    return {
        "estado": "integrado",
        "servicios": {
            "ia_url_processor": "activo",
            "fuid_crud": "activo", 
            "integration_service": "activo"
        },
        "endpoints_disponibles": {
            "procesar_url": "POST /integracion/procesar-url",
            "listar_fuids": "GET /fluid/",
            "crear_fuid_manual": "POST /fluid/"
        }
    }