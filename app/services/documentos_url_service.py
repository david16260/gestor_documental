#app/services/documentos_url_service.py
import os
import re
import hashlib
from pathlib import Path

from app.services.google_drive import (
    download_drive_file,
    download_drive_folder
)
from app.config import UPLOAD_DIR


def extract_drive_id(url: str):
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1), "file"

    m = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1), "folder"

    return None, None


def hash_file(path: Path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def process_external_document(url: str, usuario_id: int, version="1.0"):
    drive_id, tipo = extract_drive_id(url)

    documentos = []

    # Carpeta Drive
    if drive_id and tipo == "folder":
        out_dir = Path(UPLOAD_DIR) / f"user_{usuario_id}" / drive_id
        rutas = download_drive_folder(drive_id, out_dir)

        for ruta in rutas:
            path = Path(ruta)
            documentos.append({
                "nombre_archivo": path.name,
                "extension": path.suffix.replace(".", ""),
                "version": version,
                "ruta_guardado": str(path),
                "tamano_kb": round(path.stat().st_size / 1024, 2),
                "hash_archivo": hash_file(path),
                "usuario_id": usuario_id,
                "content_type": None,
                "last_modified": None,
                "servidor": "google_drive"
            })

        return documentos

    # Archivo Drive
    if drive_id and tipo == "file":
        out_dir = Path(UPLOAD_DIR) / f"user_{usuario_id}"
        out_dir.mkdir(exist_ok=True, parents=True)

        ruta = download_drive_file(drive_id, out_dir)
        path = Path(ruta)

        return [{
            "nombre_archivo": path.name,
            "extension": path.suffix.replace(".", ""),
            "version": version,
            "ruta_guardado": str(path),
            "tamano_kb": round(path.stat().st_size / 1024, 2),
            "hash_archivo": hash_file(path),
            "usuario_id": usuario_id,
            "content_type": None,
            "last_modified": None,
            "servidor": "google_drive"
        }]

    raise Exception("URL no reconocida como Drive pública.")
