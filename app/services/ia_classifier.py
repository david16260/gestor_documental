import re
from pathlib import Path
from typing import Dict, Tuple

from app.models.documento import Documento


RULES = {
    "factura": {"serie": "Finanzas", "subserie": "Facturas", "categoria": "Finanzas > Facturas"},
    "contrato": {"serie": "Legal", "subserie": "Contratos", "categoria": "Legal > Contratos"},
    "acta": {"serie": "Gobierno", "subserie": "Actas", "categoria": "Actas"},
    "informe": {"serie": "Operaciones", "subserie": "Informes", "categoria": "Reportes"},
}


def clasificar_nombre(nombre: str) -> Tuple[str, Dict]:
    lower = nombre.lower()
    for palabra, meta in RULES.items():
        if re.search(palabra, lower):
            return palabra, meta
    return "general", {"serie": "General", "subserie": "General", "categoria": "General"}


def etiquetar_documento(doc: Documento) -> Dict:
    _, meta = clasificar_nombre(doc.nombre_archivo)
    return {
        "documento_id": doc.id,
        "clasificacion": meta,
        "confianza": 0.7 if meta["serie"] != "General" else 0.3,
    }
