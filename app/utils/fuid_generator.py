import uuid
from datetime import datetime

def generate_fuid() -> str:
    """
    Genera un FUID único basado en timestamp y UUID
    Formato: FUID-YYYYMMDD-HHMMSS-UUID
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    
    return f"FUID-{timestamp}-{unique_id}"