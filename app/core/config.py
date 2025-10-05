from pathlib import Path
import mysql.connector
from mysql.connector import Error
from decouple import config

# Configuración existente
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xml", ".txt", ".json", ".xsd"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Configuración de la base de datos MySQL desde variables de entorno
DB_CONFIG = {
    'host': config('DB_HOST'),
    'user': config('DB_USER'),
    'password': config('DB_PASSWORD'),
    'database': config('DB_DATABASE')
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                version VARCHAR(50) NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                user VARCHAR(255) NOT NULL,
                saved_path VARCHAR(255) NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# Inicializa la base de datos al importar el módulo
init_db()