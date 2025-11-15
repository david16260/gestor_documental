from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verificar_rol(permisos: list):
    def wrapper(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, "CLAVE_SECRETA", algorithms=["HS256"])
            rol = payload.get("rol")

            if rol not in permisos:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permisos para acceder a este recurso"
                )

        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido")

    return wrapper