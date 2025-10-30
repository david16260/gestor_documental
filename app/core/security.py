import hashlib
from jose import JWTError, jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta

# Configuración JWT (debes usar las mismas que en auth.py)
SECRET_KEY = "mi_clave_secreta_para_jwt"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Devuelve el hash MD5 de la contraseña."""
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""
    return hash_password(password) == hashed

def verificar_token(token: str) -> dict:
    """
    Verifica y decodifica un token JWT.
    Retorna el payload si es válido, lanza excepción si no.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception