import hashlib

def hash_password(password: str) -> str:
    """Devuelve el hash MD5 de la contraseña."""
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""
    return hash_password(password) == hashed
