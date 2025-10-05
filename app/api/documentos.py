from fastapi import APIRouter, UploadFile, File, HTTPException
from io import BytesIO
from pathlib import Path
import hashlib
import json
from lxml import etree
from jsonschema import validate, ValidationError
from app.core.config import get_db_connection, ALLOWED_EXTENSIONS, MAX_SIZE_BYTES, UPLOAD_DIR
from app.models.documento import UploadResponse

print(f"Extensiones permitidas cargadas: {ALLOWED_EXTENSIONS}")  # Depuración

router = APIRouter()

def file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")

    contents = await file.read()
    size = len(contents)
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx 10MB)")

    # Validación específica por tipo
    if ext == '.xml':
        try:
            print(f"Contenido XML crudo: {contents.decode('utf-8')}")
            xml_tree = etree.parse(BytesIO(contents))
            print(f"Cargando XSD desde: {Path('app/schemas/document.xsd').resolve()}")
            with open('app/schemas/document.xsd', 'r', encoding='utf-8') as f:
                xsd_content = f.read()
            print(f"Contenido XSD crudo: {xsd_content}")
            xsd_tree = etree.parse(BytesIO(xsd_content.encode('utf-8')))
            xsd = etree.XMLSchema(xsd_tree)
            if not xsd.validate(xml_tree):
                raise HTTPException(status_code=400, detail="Estructura XML inválida según XSD")
        except etree.XMLSyntaxError as e:
            print(f"Error de sintaxis XML: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error de sintaxis XML: {str(e)}")
        except Exception as e:
            print(f"Error en validación XML: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error en validación XML: {str(e)}")

    elif ext == '.json':
        try:
            print(f"Contenido JSON crudo: {contents.decode('utf-8')}")
            data = json.loads(contents)
            with open('app/schemas/document_schema.json', 'r', encoding='utf-8') as f:
                schema_content = f.read()
            print(f"Contenido Schema JSON crudo: {schema_content}")
            schema = json.loads(schema_content)
            validate(instance=data, schema=schema)
        except json.JSONDecodeError as e:
            print(f"Error JSON: {e}")
            raise HTTPException(status_code=400, detail="JSON inválido")
        except ValidationError as e:
            print(f"Error de validación: {e.message}")
            raise HTTPException(status_code=400, detail=f"Error de validación JSON Schema: {e.message}")
        except Exception as e:
            print(f"Error inesperado: {e}")
            raise HTTPException(status_code=400, detail=f"Error en validación JSON: {str(e)}")

    # Generar versión
    version = file_hash(contents)[:8]
    # Obtener usuario
    user = "root"

    # Proceder con hash y guardado
    hash_value = file_hash(contents)
    hash_path = UPLOAD_DIR / f"{hash_value}{ext}"
    duplicate = hash_path.exists()

    if not duplicate:
        with open(hash_path, "wb") as f:
            f.write(contents)

    # Guardar en MySQL
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO file_logs (filename, version, user, saved_path) VALUES (%s, %s, %s, %s)",
            (file.filename, version, user, str(hash_path))
        )
        conn.commit()
        conn.close()
    else:
        raise HTTPException(status_code=500, detail="Error connecting to database")

    return UploadResponse(
        filename=file.filename,
        size_kb=round(size / 1024, 2),
        duplicate=duplicate,
        saved_path=str(hash_path)
    )