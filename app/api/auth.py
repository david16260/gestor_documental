# app/api/auth.py
from fastapi import APIRouter, Form, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.models.usuario import Usuario
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from fastapi import Form
from datetime import datetime, timedelta
import secrets
from pydantic import BaseModel

# ===================================
# CONFIGURACIÓN JWT
# ===================================
SECRET_KEY = "mi_clave_secreta_para_jwt"  # puedes moverlo a .env
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
    user_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if user_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=hash_password(password)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email
    }

# ===================================
# GENERAR TOKEN JWT
# ===================================
def crear_token_jwt(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ===================================
# LOGIN (DEVUELVE TOKEN)
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

    # Crear token JWT
    access_token = crear_token_jwt(data={"sub": str(usuario.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario.nombre
    }

# ===================================
# OBTENER USUARIO ACTUAL (Protección JWT)
# ===================================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = req.email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Generar token aleatorio y expiración
    token = secrets.token_urlsafe(32)
    expiracion = datetime.utcnow() + timedelta(minutes=30)  # 30 min de validez
    usuario.reset_token = token
    usuario.reset_token_exp = expiracion

    db.commit()

    # Aquí normalmente envías email, pero en desarrollo solo devolvemos el token
    return {
        "mensaje": f"Token generado. Usar para restablecer contraseña en /reset-password",
        "reset_token": token
    }

# 2️⃣ Restablecer contraseña usando token
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
