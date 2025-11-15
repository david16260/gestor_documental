# app/api/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.usuario import Usuario
from app.api.auth import require_role, get_current_user

router = APIRouter(prefix="/users", tags=["Usuarios"])


# ======================================================
# LISTAR TODOS LOS USUARIOS (solo admin)
# ======================================================
@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))  # Protección por rol
):
    usuarios = db.query(Usuario).all()

    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "rol": u.rol
        }
        for u in usuarios
    ]


# ======================================================
# OBTENER PERFIL DEL USUARIO LOGUEADO
# ======================================================
@router.get("/me")
def get_my_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "email": current_user.email,
        "rol": current_user.rol
    }


# ======================================================
# OBTENER UN USUARIO POR ID (admin o el mismo usuario)
# ======================================================
@router.get("/{id_usuario}")
def get_user(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si no eres admin, solo puedes ver tu propio perfil
    if current_user.rol != "admin" and current_user.id != usuario.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol
    }


# ======================================================
# ACTUALIZAR DATOS PERSONALES (solo el dueño del perfil)
# ======================================================
@router.put("/{id_usuario}")
def update_user(
    id_usuario: int,
    nombre: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Solo el dueño puede modificar su perfil
    if current_user.id != id_usuario:
        raise HTTPException(status_code=403, detail="No puedes modificar este usuario")

    usuario.nombre = nombre
    db.commit()
    db.refresh(usuario)

    return {"mensaje": "Usuario actualizado correctamente"}


# ======================================================
# ASIGNAR ROL A UN USUARIO (solo admin)
# ======================================================
@router.put("/asignar-rol/{id_usuario}")
def asignar_rol(
    id_usuario: int,
    rol: str,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if rol not in ["admin", "usuario", "super"]:
        raise HTTPException(status_code=400, detail="Rol inválido")

    usuario.rol = rol
    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Rol actualizado correctamente",
        "id": usuario.id,
        "nuevo_rol": usuario.rol
    }


# ======================================================
# ELIMINAR USUARIO (solo admin)
# ======================================================
@router.delete("/{id_usuario}")
def delete_user(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()

    return {"mensaje": "Usuario eliminado correctamente"}