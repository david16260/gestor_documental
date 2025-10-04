from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xml", ".txt", ".json", ".xsd"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB