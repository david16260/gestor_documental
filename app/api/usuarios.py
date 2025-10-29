from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.usuario import Usuario
from app.api.auth import get_current_user, require_role


router = APIRouter(prefix="/users", tags=["Usuarios"])


# Listar todos los usuarios — sólo ADMIN
@router.get("/")
def list_users(db: Session = Depends(get_db), admin: Usuario = Depends(require_role("admin"))):
users = db.query(Usuario).all()
return [{"id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol} for u in users]


# Cambiar rol de un usuario — sólo ADMIN
@router.put("/{user_id}/role")
def change_role(user_id: int, new_role: str, db: Session = Depends(get_db), admin: Usuario = Depends(require_role("admin"))):
user = db.query(Usuario).filter(Usuario.id == user_id).first()
if not user:
raise HTTPException(status_code=404, detail="Usuario no encontrado")
user.rol = new_role
db.commit()
return {"id": user.id, "email": user.email, "rol": user.rol}
