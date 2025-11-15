from pathlib import Path
from fastapi import UploadFile
from app.api.documentos import upload_file as upload_endpoint
from app.utils.reportes import generar_reporte_errores
from io import BytesIO

def ingesta_local(carpeta: str, usuario_id: int, db):
    """
    HU3: Lee todos los archivos de una carpeta local y los sube al sistema.
    HU5: Genera reporte de errores (duplicados o corruptos)
    """
    folder = Path(carpeta)
    errores = []

    for file_path in folder.iterdir():
        if file_path.is_file():
            with open(file_path, "rb") as f:
                upload_file_obj = UploadFile(filename=file_path.name, file=f)
                try:
                    upload_endpoint(file=upload_file_obj, usuario_id=usuario_id, db=db)
                except Exception as e:
                    errores.append({
                        "nombre_archivo": file_path.name,
                        "tipo_error": "duplicado/corrupto",
                        "detalle": str(e)
                    })

    if errores:
        reporte = generar_reporte_errores(errores)
        print(f"Reporte de errores generado: {reporte}")


def ingesta_sharepoint(lista_archivos: list, usuario_id: int, db):
    """
    HU3: Ingesta desde SharePoint
    lista_archivos: list of tuples (nombre_archivo, contenido_bytes)
    """
    errores = []

    for nombre, contenido in lista_archivos:
        upload_file_obj = UploadFile(filename=nombre, file=BytesIO(contenido))
        try:
            upload_endpoint(file=upload_file_obj, usuario_id=usuario_id, db=db)
        except Exception as e:
            errores.append({
                "nombre_archivo": nombre,
                "tipo_error": "duplicado/corrupto",
                "detalle": str(e)
            })

    if errores:
        reporte = generar_reporte_errores(errores)
        print(f"Reporte de errores generado: {reporte}")
