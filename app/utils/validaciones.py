# app/utils/validaciones.py
import zipfile
from pathlib import Path
from PyPDF2 import PdfReader

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

def tiene_firma_digital(path: str) -> bool:
    """
    Verifica si un archivo PDF contiene una firma digital.
    Retorna True si se detecta una firma, False en caso contrario.
    """
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            if "/Annots" in page:
                annots = page["/Annots"]
                for annot in annots:
                    obj = annot.get_object()
                    if obj.get("/Subtype") == "/Widget" and obj.get("/FT") == "/Sig":
                        return True
        return False
    except Exception:
        return False
