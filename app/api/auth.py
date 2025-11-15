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
        rol="usuario"  # Rol por defecto del archivo 2
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email,
        "rol": nuevo_usuario.rol  # Incluir rol en respuesta
    }

# ===================================
# GENERAR TOKEN JWT (FUNCIÓN UNIFICADA)
# ===================================
def crear_token_jwt(data: dict, expires_delta: timedelta | None = None):
    """
    Función unificada para generar tokens JWT
    Compatible con ambos enfoques de los archivos originales
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Alias para compatibilidad
generar_token = crear_token_jwt

# ===================================
# LOGIN (DEVUELVE TOKEN - VERSIÓN MEJORADA)
# ===================================
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # Crear token JWT con información mejorada (combinando ambos enfoques)
    access_token = crear_token_jwt(data={
        "sub": str(usuario.id),  # Del archivo 1
        "email": usuario.email,  # Del archivo 2
        "rol": usuario.rol       # Del archivo 2
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario.nombre,  # Del archivo 1
        "rol": usuario.rol          # Del archivo 2
    }

# ===================================
# OBTENER USUARIO ACTUAL (VERSIÓN ROBUSTA)
# ===================================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Compatibilidad con ambos formatos de token
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if user_id:
            # Formato del archivo 1: sub contiene el ID
            user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
        elif email:
            # Formato del archivo 2: sub contiene el email
            user = db.query(Usuario).filter(Usuario.email == email).first()
        else:
            raise credentials_exception
            
        if user is None:
            raise credentials_exception
        return user
        
    except JWTError:
        raise credentials_exception

# ===================================
# MIDDLEWARE DE ROLES (DEL ARCHIVO 2)
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

    # Generar token aleatorio y expiración
    token = secrets.token_urlsafe(32)
    expiracion = datetime.utcnow() + timedelta(minutes=30)  # 30 min de validez

    usuario.reset_token = token
    usuario.reset_token_exp = expiracion

    db.commit()

    # Mensaje combinado de ambos archivos
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

    # Actualizar contraseña y limpiar token
    usuario.password_hash = hash_password(nueva_password)
    usuario.reset_token = None
    usuario.reset_token_exp = None

    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}