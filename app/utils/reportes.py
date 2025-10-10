# app/utils/reportes.py
import csv
from pathlib import Path
from datetime import datetime

REPORTE_DIR = Path("reportes")
REPORTE_DIR.mkdir(exist_ok=True)

def generar_reporte_errores(errores: list):
    """
    errores: lista de dicts con keys:
    - nombre_archivo
    - tipo_error ('duplicado', 'corrupto', etc)
    - detalle
    """
    ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    reporte_file = REPORTE_DIR / f"reporte_errores_{ahora}.csv"

    with open(reporte_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nombre_archivo", "tipo_error", "detalle"])
        writer.writeheader()
        for e in errores:
            writer.writerow(e)

    return str(reporte_file)
