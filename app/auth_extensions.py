from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException
from jose import jwt

SECRET_KEY = "change_this_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

def crear_token_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def require_role(*allowed_roles):
    def _require_role(current_user = Depends(lambda: None)):
        if current_user is None:
            raise HTTPException(status_code=401, detail="No autenticado")
        user_role = getattr(current_user, 'rol', None)
        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este recurso")
        return current_user
    return _require_role
