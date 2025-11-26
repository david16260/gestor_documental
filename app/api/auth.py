from datetime import datetime, timedelta
import secrets

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(tags=["Autenticación"])


class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/register")
def register(
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=hash_password(password),
        rol="usuario",
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email,
        "rol": nuevo_usuario.rol,
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    access_token = create_access_token(
        data={"sub": str(usuario.id), "email": usuario.email, "rol": usuario.rol},
        expires_delta=settings.access_token_expire_minutes,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario.nombre,
        "rol": usuario.rol,
    }


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exception

    user_id = payload.get("sub")
    email = payload.get("email")

    if user_id:
        user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    elif email:
        user = db.query(Usuario).filter(Usuario.email == email).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user


def require_role(*allowed_roles):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso",
            )
        return current_user

    return role_checker


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == req.email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    token = secrets.token_urlsafe(32)
    expiracion = datetime.utcnow() + timedelta(minutes=30)

    usuario.reset_token = token
    usuario.reset_token_exp = expiracion

    db.commit()

    return {
        "mensaje": "Token generado. Úselo en /reset-password",
        "reset_token": token,
    }


@router.post("/reset-password")
def reset_password(
    token: str = Form(...),
    nueva_password: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.reset_token == token).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Token inválido")

    if usuario.reset_token_exp is None or usuario.reset_token_exp < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expirado")

    usuario.password_hash = hash_password(nueva_password)
    usuario.reset_token = None
    usuario.reset_token_exp = None

    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}
