# app/utils/validaciones.py
import zipfile
from pathlib import Path

def validar_trd_ccd(file_path: Path) -> bool:
    """
    Valida la estructura de un archivo TRD/CCD.
    Retorna True si es válido, False si no.
    """
    # Ejemplo: si fuera un ZIP con archivos específicos
    if file_path.suffix == ".zip":
        with zipfile.ZipFile(file_path, 'r') as zipf:
            nombres = zipf.namelist()
            # Validamos que contenga los archivos obligatorios
            if "metadata.xml" in nombres and "documentos/" in nombres[0]:
                return True
        return False
    # Si fuera otro formato, se agregan validaciones aquí
    return True  # Por defecto, válido
