import os
import hashlib
import requests
import re
import uuid
from pathlib import Path
from app.config import UPLOAD_DIR


def detect_google_file_type(url: str):
    """
    Detecta el tipo de archivo de Google y retorna el formato de exportación apropiado
    """
    if "spreadsheets" in url or "spreadsheet" in url:
        return "xlsx"
    elif "document" in url:
        return "pdf" 
    elif "presentation" in url or "slides" in url:
        return "pdf"
    elif "drive.google.com" in url:
        if any(ext in url.lower() for ext in ['.xlsx', '.xls', '.csv']):
            return "xlsx"
        elif any(ext in url.lower() for ext in ['.doc', '.docx', '.pdf']):
            return "pdf"
    return "pdf"


def normalize_google_url(url: str, desired_format=None):
    """
    Convierte URLs de Google Drive/Sheets/Docs en descarga directa.
    """
    print(f"DEBUG: Normalizando URL: {url}")

    if not desired_format:
        desired_format = detect_google_file_type(url)

    # Google Sheets
    if "docs.google.com/spreadsheets" in url or "spreadsheet" in url:
        if "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format={desired_format}"
        elif "key=" in url:
            file_id = url.split("key=")[1].split("&")[0]
            return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format={desired_format}"

    # Google Docs
    elif "docs.google.com/document" in url:
        if "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/document/d/{file_id}/export?format=pdf"

    # Google Slides  
    elif "docs.google.com/presentation" in url:
        if "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/presentation/d/{file_id}/export/pdf"

    # Drive files
    elif "drive.google.com/file/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    elif "drive.google.com/open" in url and "id=" in url:
        file_id = url.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    elif "uc?id=" in url:
        return url.replace("uc?id=", "uc?export=download&id=")

    print(f"DEBUG: URL no reconocida como Google, retornando original")
    return url


def sanitize_filename(filename: str) -> str:
    """
    Limpia el nombre del archivo para Windows
    """
    if not filename:
        return "documento_sin_nombre.bin"
    
    filename = filename.split(';')[0]
    filename = filename.split('"')[0] if '"' in filename else filename
    
    if "filename*=" in filename:
        filename = filename.split("filename*=")[0]
    
    invalid_chars = '<>:"/\\|?*\''
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    filename = re.sub(r'\s+', ' ', filename).strip()
    
    if not filename or filename in ('export', 'download', 'unnamed', 'undefined'):
        return f"documento_{uuid.uuid4().hex[:8]}.bin"
    
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200 - len(ext)] + ext
    
    return filename


def download_google_file(url: str, headers: dict):
    """
    Función especializada para descargar archivos de Google
    con manejo de confirmación para archivos grandes.
    """
    session = requests.Session()
    session.headers.update(headers)
    
    # Primera solicitud
    response = session.get(url, allow_redirects=True, timeout=30)
    
    # Si es un archivo grande de Google Drive, puede requerir confirmación
    if response.status_code == 200 and "text/html" in response.headers.get("Content-Type", ""):
        content = response.text.lower()
        
        # Buscar el formulario de confirmación de Google Drive
        if "confirm" in content and "google" in content:
            print("DEBUG: Google requiere confirmación, procesando formulario...")
            
            # Extraer token de confirmación
            token_match = re.search(r'name="confirm" value="([^"]+)"', content)
            if token_match:
                confirm_token = token_match.group(1)
                download_url = f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={url.split('id=')[-1]}"
                response = session.get(download_url, allow_redirects=True, timeout=30)
    
    return response


def process_external_document(url: str, usuario_id: int, version: str = "1.0"):
    """
    Descarga un archivo desde la URL pública, lo guarda en /uploads
    y retorna la info necesaria para BD.
    """
    try:
        print(f"DEBUG: URL original recibida: {url}")

        # 1) Normalizar URL
        original_url = url
        url = normalize_google_url(url)
        print(f"DEBUG: URL normalizada: {url}")

        # 2) Headers mejorados para Google
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # 3) Intentar descarga con diferentes estrategias
        response = None
        
        # Estrategia 1: Descarga directa
        try:
            print("DEBUG: Intentando descarga directa...")
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            print(f"DEBUG: Status Code (directo): {response.status_code}")
        except Exception as e:
            print(f"DEBUG: Error en descarga directa: {e}")

        # Estrategia 2: Si falla o es Google, usar sesión
        if not response or response.status_code != 200:
            print("DEBUG: Intentando con sesión...")
            try:
                session = requests.Session()
                session.headers.update(headers)
                response = session.get(url, timeout=30, allow_redirects=True)
                print(f"DEBUG: Status Code (sesión): {response.status_code}")
            except Exception as e:
                print(f"DEBUG: Error en sesión: {e}")

        # Estrategia 3: Si es Google y sigue fallando, usar función especializada
        if ("google.com" in url) and (not response or response.status_code != 200):
            print("DEBUG: Usando función especializada para Google...")
            try:
                response = download_google_file(url, headers)
                print(f"DEBUG: Status Code (especializado): {response.status_code}")
            except Exception as e:
                print(f"DEBUG: Error en función especializada: {e}")

        # Verificar si alguna estrategia funcionó
        if not response or response.status_code != 200:
            error_msg = f"No fue posible descargar el archivo. Status: {response.status_code if response else 'No response'}. Verifica que el archivo sea público."
            print(f"DEBUG: {error_msg}")
            raise Exception(error_msg)

        # 4) Verificar que la respuesta tenga contenido
        if len(response.content) == 0:
            raise Exception("El archivo descargado está vacío")

        print(f"DEBUG: Descarga exitosa. Tamaño: {len(response.content)} bytes")
        print(f"DEBUG: Content-Type: {response.headers.get('Content-Type')}")

        # 5) Obtener y limpiar nombre del archivo
        content_disp = response.headers.get("Content-Disposition", "")
        filename = None

        if "filename=" in content_disp:
            if "filename*=" in content_disp:
                filename_part = content_disp.split("filename*=")[-1]
                if "''" in filename_part:
                    filename = filename_part.split("''")[-1]
                else:
                    filename = filename_part.split(";")[0]
            else:
                filename = content_disp.split("filename=")[-1].split(";")[0]
            
            filename = filename.strip().strip('"').strip("'")
        
        if not filename:
            filename = url.split("/")[-1].split("?")[0]
            if not filename or filename == "export":
                content_type = response.headers.get("Content-Type", "")
                if "spreadsheet" in url or "xlsx" in content_type:
                    filename = "spreadsheet.xlsx"
                elif "document" in url or "pdf" in content_type:
                    filename = "document.pdf"
                else:
                    filename = "download.bin"

        # Limpiar nombre
        original_filename = filename
        filename = sanitize_filename(filename)
        print(f"DEBUG: Nombre original: {original_filename}")
        print(f"DEBUG: Nombre limpio: {filename}")

        # 6) Asegurar extensión
        if "." not in filename:
            content_type = response.headers.get("Content-Type", "").lower()
            ext_map = {
                'application/pdf': '.pdf',
                'application/vnd.ms-excel': '.xls',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                'application/msword': '.doc',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'text/plain': '.txt',
                'text/csv': '.csv',
                'application/octet-stream': '.bin'
            }
            
            extension = '.bin'
            for content, ext in ext_map.items():
                if content in content_type:
                    extension = ext
                    break
            
            if "spreadsheets" in original_url and extension == '.bin':
                extension = '.xlsx'
            
            filename += extension

        # 7) Crear directorio y guardar
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        storage_path = Path(UPLOAD_DIR) / filename
        
        try:
            with open(storage_path, "wb") as f:
                f.write(response.content)
            print(f"DEBUG: Archivo guardado en: {storage_path}")
        except (OSError, IOError) as e:
            print(f"DEBUG: Error guardando archivo: {e}")
            safe_name = f"doc_{uuid.uuid4().hex[:8]}{os.path.splitext(filename)[1]}"
            storage_path = Path(UPLOAD_DIR) / safe_name
            with open(storage_path, "wb") as f:
                f.write(response.content)
            filename = safe_name

        # 8) Calcular hash y metadatos
        file_hash = hashlib.sha256(response.content).hexdigest()

        metadata_extra = {
            "content_type": response.headers.get("Content-Type"),
            "last_modified": response.headers.get("Last-Modified"),
            "servidor": response.headers.get("Server"),
            "nombre_original": original_filename,
            "url_original": original_url
        }

        # 9) Retornar resultado
        result = {
            "nombre_archivo": filename,
            "extension": filename.split(".")[-1] if "." in filename else "",
            "version": version,
            "ruta_guardado": str(storage_path),
            "tamano_kb": round(len(response.content) / 1024, 2),
            "hash_archivo": file_hash,
            "usuario_id": usuario_id,
            **metadata_extra
        }
        
        print(f"DEBUG: Proceso completado exitosamente")
        return result

    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}. Verifica la URL y que el archivo sea público."
        print(f"DEBUG: {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error procesando documento: {str(e)}"
        print(f"DEBUG: {error_msg}")
        raise Exception(error_msg)