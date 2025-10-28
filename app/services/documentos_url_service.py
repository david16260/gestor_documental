import os
import hashlib
import requests
from pathlib import Path
from app.config import UPLOAD_DIR
from PyPDF2 import PdfReader

try:
    import magic
    mime = magic.Magic(mime=True)
except ImportError:
    mime = None

def normalize_google_url(url: str, desired_format="xlsx"):
    if "docs.google.com" in url:
        if "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
            if "spreadsheets" in url:
                return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format={desired_format}"
            if "document" in url:
                return f"https://docs.google.com/document/d/{file_id}/export?format=pdf"
    if "drive.google.com/file/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    if "uc?id=" in url:
        return url.replace("uc?id=", "uc?export=download&id=")
    return url

def process_external_document(url: str, usuario_id: int, version: str = "1.0"):
    try:
        url = normalize_google_url(url)
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception("No fue posible descargar el archivo (URL inválida o privada).")

        content_disp = response.headers.get("Content-Disposition", "")
        filename = None

        if "filename=" in content_disp:
            filename = content_disp.split("filename=")[-1].strip().strip('"')
        else:
            filename = url.split("/")[-1]

        if filename.lower() in ("export", "download", ""):
            filename += ".bin"

        if "." not in filename:
            guessed_ext = response.headers.get("Content-Type", "").split("/")[-1]
            filename += f".{guessed_ext}"

        extension = filename.split(".")[-1].lower()

        storage_path = Path(UPLOAD_DIR) / filename
        with open(storage_path, "wb") as f:
            f.write(response.content)

        file_hash = hashlib.sha256(response.content).hexdigest()

        content_type = response.headers.get("Content-Type", "")
        last_modified = response.headers.get("Last-Modified", "")
        servidor = response.headers.get("Server", "")

        categoria = "General"
        confidencialidad = "Media"
        tipo_documento = "Otro"
        autor = None

        if "factura" in filename.lower():
            categoria = "Finanzas > Facturas"
            confidencialidad = "Alta"
            tipo_documento = "Factura"
        elif "contrato" in filename.lower():
            categoria = "Legal > Contratos"
            confidencialidad = "Confidencial"
            tipo_documento = "Contrato"
        elif extension in {"jpg", "png"}:
            categoria = "Imágenes"
            tipo_documento = "Imagen"
        elif extension == "pdf":
            tipo_documento = "PDF"
            try:
                reader = PdfReader(str(storage_path))
                if reader.metadata:
                    autor = reader.metadata.get("/Author") or reader.metadata.get("Author")
            except Exception:
                pass
        elif extension == "docx":
            tipo_documento = "Word"
        elif extension == "xlsx":
            tipo_documento = "Excel"

        tipo_mime = "desconocido"
        if mime:
            try:
                tipo_mime = mime.from_file(str(storage_path))
            except Exception:
                pass

        return {
            "nombre_archivo": filename,
            "extension": extension,
            "version": version,
            "ruta_guardado": str(storage_path),
            "tamano_kb": round(len(response.content) / 1024, 2),
            "hash_archivo": file_hash,
            "usuario_id": usuario_id,
            "content_type": tipo_mime,
            "last_modified": last_modified,
            "servidor": servidor,
            "tipo_documento": tipo_documento,
            "categoria": categoria,
            "confidencialidad": confidencialidad,
            "autor": autor
        }

    except requests.exceptions.RequestException:
        raise Exception("Error al conectar con la URL (no hay acceso o requiere login).")
    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")
