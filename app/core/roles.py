from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verificar_rol(permisos: list):
    def wrapper(token: str = Depends(oauth2_scheme)):
        payload = decode_token(token)
        rol = payload.get("rol")

        if rol not in permisos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso",
            )

    return wrapper
