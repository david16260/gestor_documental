from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
try:
    from app.models.usuario import Usuario
except Exception:
    from app.models import usuario as usuario_model
    Usuario = usuario_model.Usuario

try:
    from app.api.auth import require_role
except Exception:
    from app.auth_extensions import require_role

router = APIRouter(prefix="/users", tags=["Usuarios"])

@router.get("/")
def list_users(db: Session = Depends(get_db), admin = Depends(require_role("admin"))):
    users = db.query(Usuario).all()
    return [{"id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol} for u in users]

#se agrego el endpoint psara asignar roles

@router.put("/asignar_rol/{id_usuario}")
def asignar_rol(id_usuario: int, rol: str, 
                db: Session = Depends(get_db),
                permiso = Depends(verificar_rol(["admin"]))):

    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.rol = rol
    db.commit()

    return {"mensaje": f"Rol actualizado a {rol}"}

