import os
import hashlib
import requests
from pathlib import Path
from app.config import UPLOAD_DIR


def normalize_google_url(url: str, desired_format="xlsx"):
    """
    Convierte URLs de Google Drive/Sheets/Docs en descarga directa.
    Soporta:
    - Google Sheets -> XLSX
    - Google Docs -> PDF
    - Drive /file/d/<id>/view
    - Drive uc?id=<id>
    """

    # Google Sheets o Google Docs
    if "docs.google.com" in url:
        if "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]

            if "spreadsheets" in url:
                return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format={desired_format}"

            if "document" in url:
                return f"https://docs.google.com/document/d/{file_id}/export?format=pdf"

    # Drive: https://drive.google.com/file/d/<id>/view
    if "drive.google.com/file/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # Drive uc?id=<id>
    if "uc?id=" in url:
        return url.replace("uc?id=", "uc?export=download&id=")

    return url
    


def process_external_document(url: str, usuario_id: int, version: str = "1.0"):
    """
    Descarga un archivo desde la URL pública, lo guarda en /uploads
    y retorna la info necesaria para BD.
    """
    try:
        # 1) Normalizar URL si es Google
        url = normalize_google_url(url)

        # 2) Descargar archivo
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception("No fue posible descargar el archivo (URL inválida o privada).")

        # 3) Obtener nombre
        content_disp = response.headers.get("Content-Disposition", "")
        filename = None

        if "filename=" in content_disp:
            filename = content_disp.split("filename=")[-1].strip().strip('"')
        else:
            filename = url.split("/")[-1]

        # Evitar nombres como 'export'
        if filename.lower() in ("export", "download", ""):
            filename += ".bin"

        # Asegurar extensión
        if "." not in filename:
            guessed_ext = response.headers.get("Content-Type", "").split("/")[-1]
            filename += f".{guessed_ext}"

        extension = filename.split(".")[-1]

        # 4) Guardar archivo
        storage_path = Path(UPLOAD_DIR) / filename
        with open(storage_path, "wb") as f:
            f.write(response.content)

        # 5) Hash
        file_hash = hashlib.sha256(response.content).hexdigest()

        # 6) Metadatos extra HTTP
        metadata_extra = {
            "content_type": response.headers.get("Content-Type"),
            "last_modified": response.headers.get("Last-Modified"),
            "servidor": response.headers.get("Server")
        }

        # 7) Retorno al router
        return {
            "nombre_archivo": filename,
            "extension": extension,
            "version": version,
            "ruta_guardado": str(storage_path),
            "tamano_kb": round(len(response.content) / 1024, 2),
            "hash_archivo": file_hash,
            "usuario_id": usuario_id,
            **metadata_extra
        }

    except requests.exceptions.RequestException:
        raise Exception("Error al conectar con la URL (no hay acceso o requiere login).")
    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")
