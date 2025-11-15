#app/utils/hash_generator.py
import hashlib
import json
from datetime import datetime

def generate_hash(data: dict) -> str:
    """
    Genera un hash único para el FUID basado en los datos
    """
    data_str = json.dumps(data, sort_keys=True) + str(datetime.now().timestamp())
    return hashlib.sha256(data_str.encode()).hexdigest()