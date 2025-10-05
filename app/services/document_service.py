from io import BytesIO
from pathlib import Path
import json
import logging
from lxml import etree
from jsonschema import validate, ValidationError
from fastapi import HTTPException
from app.utils.hashing import file_hash
from app.core.config import get_db_connection, ALLOWED_EXTENSIONS, MAX_SIZE_BYTES, UPLOAD_DIR

logger = logging.getLogger(__name__)

def validar_xml(contents: bytes):
    try:
        logger.info("Validando XML...")
        xml_tree = etree.parse(BytesIO(contents))
        with open('app/schemas/document.xsd', 'r', encoding='utf-8') as f:
            xsd_content = f.read()
        xsd_tree = etree.parse(BytesIO(xsd_content.encode('utf-8')))
        xsd = etree.XMLSchema(xsd_tree)
        if not xsd.validate(xml_tree):
            raise HTTPException(status_code=400, detail="Estructura XML inválida según XSD")
    except etree.XMLSyntaxError as e:
        logger.error(f"Error de sintaxis XML: {e}")
        raise HTTPException(status_code=400, detail=f"Error de sintaxis XML: {str(e)}")
    except Exception as e:
        logger.error(f"Error general validando XML: {e}")
        raise HTTPException(status_code=400, detail=f"Error en validación XML: {str(e)}")


def validar_json(contents: bytes):
    try:
        logger.info("Validando JSON...")
        data = json.loads(contents)
        with open('app/schemas/document_schema.json', 'r', encoding='utf-8') as f:
            schema_content = f.read()
        schema = json.loads(schema_content)
        validate(instance=data, schema=schema)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON inválido")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Error de validación JSON Schema: {e.message}")
    except Exception as e:
        logger.error(f"Error general validando JSON: {e}")
        raise HTTPException(status_code=400, detail=f"Error en validación JSON: {str(e)}")


def procesar_documento(file):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")

    contents = file.file.read()
    size = len(contents)
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx 10MB)")

    # Validar estructura
    if ext == ".xml":
        validar_xml(contents)
    elif ext == ".json":
        validar_json(contents)

    # Calcular hash
    hash_value = file_hash(contents)
    hash_path = UPLOAD_DIR / f"{hash_value}{ext}"
    duplicate = hash_path.exists()

    # Guardar si no existe
    if not duplicate:
        with open(hash_path, "wb") as f:
            f.write(contents)

    # Registrar en BD
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        version = hash_value[:8]
        user = "root"
        cursor.execute(
            "INSERT INTO file_logs (filename, version, user, saved_path) VALUES (%s, %s, %s, %s)",
            (file.filename, version, user, str(hash_path))
        )
        conn.commit()
        conn.close()
    else:
        raise HTTPException(status_code=500, detail="Error connecting to database")

    return {
        "filename": file.filename,
        "size_kb": round(size / 1024, 2),
        "duplicate": duplicate,
        "saved_path": str(hash_path)
    }
