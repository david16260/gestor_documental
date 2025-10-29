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

@router.put("/{user_id}/role")
def change_role(user_id: int, new_role: str, db: Session = Depends(get_db), admin = Depends(require_role("admin"))):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.rol = new_role
    db.commit()
    return {"id": user.id, "email": user.email, "rol": user.rol}
