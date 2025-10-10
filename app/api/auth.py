# app/api/auth.py
from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.core.database import get_db
from app.core.security import hash_password, verify_password

router = APIRouter(tags=["Autenticación"])

@router.post("/register")
def register(
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar si el usuario ya existe
    user_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if user_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Crear nuevo usuario con hash de contraseña
    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=hash_password(password)  # ← usar `password` directamente
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email
    }

#-----------------------------
# Login
# -----------------------------
@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {
        "mensaje": f"Bienvenido {usuario.nombre}"
    }
