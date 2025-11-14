# app/api/auth.py
from fastapi import (
    APIRouter, Form, HTTPException, Depends, status
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import secrets

# MODELOS Y UTILIDADES
from app.models.usuario import Usuario
from app.core.database import get_db
from app.core.security import hash_password, verify_password

# ===================================
# CONFIGURACIÓN JWT
# ===================================
SECRET_KEY = "mi_clave_secreta_para_jwt"  # mover a .env en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(tags=["Autenticación"])


# ===================================
# REGISTRO DE USUARIOS
# ===================================
@router.post("/register")
def register(
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=hash_password(password),
        rol="usuario"  # Rol por defecto
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email,
        "rol": nuevo_usuario.rol
    }


# ===================================
# GENERAR TOKEN JWT
# ===================================
def generar_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ===================================
# LOGIN (DEVUELVE TOKEN)
# ===================================
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    token = generar_token({
        "sub": usuario.email,
        "id": usuario.id,
        "rol": usuario.rol
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario.rol
    }


# ===================================
# OBTENER USUARIO ACTUAL
# ===================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    cred_except = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise cred_except
    except JWTError:
        raise cred_except

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise cred_except

    return usuario


# ===================================
# MIDDLEWARE DE ROLES
# ===================================
def require_role(*allowed_roles):
    """
    Protege rutas según roles permitidos.
    Uso:
    Depends(require_role("admin"))
    """
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso"
            )
        return current_user

    return role_checker


# ===================================
# RECUPERAR CONTRASEÑA
# ===================================
class ForgotPasswordRequest(BaseModel):
    email: str


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
        "reset_token": token
    }


# ===================================
# RESTABLECER CONTRASEÑA
# ===================================
@router.post("/reset-password")
def reset_password(
    token: str = Form(...),
    nueva_password: str = Form(...),
    db: Session = Depends(get_db)
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
