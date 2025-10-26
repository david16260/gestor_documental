from sqlalchemy.orm import Session
from app.services.fuid_service import FUIDService
from app.services.documentos_url_service import process_external_document
import logging

logger = logging.getLogger(__name__)

class IntegrationService:
    def __init__(self, db: Session):
        self.db = db
        self.fuid_service = FUIDService(db)
    
    def procesar_url_y_crear_fuid(self, url: str, expediente_id: int, usuario_id: int, version: str = "1.0"):
        """
        Servicio unificado que:
        1. Usa la IA para descargar y procesar la URL (como antes)
        2. Crea automáticamente un FUID con la metadata
        3. Mantiene la misma respuesta original + añade info del FUID
        """
        try:
            # 1. PROCESAR URL CON LA IA (sin modificar - funciona igual que antes)
            resultado_ia = process_external_document(url, usuario_id, version)
            
            # 2. ENRIQUECER METADATA PARA FUID
            metadatos_fuid = self._enriquecer_metadata_fuid(resultado_ia, url)
            
            # 3. CREAR FUID AUTOMÁTICAMENTE (nueva funcionalidad)
            fuid = self.fuid_service.create_fuid(
                expediente_id=expediente_id,
                usuario_id=usuario_id,
                metadatos_fuid=metadatos_fuid,
                referencia_contenido=resultado_ia["ruta_guardado"]
            )
            
            logger.info(f"FUID creado automáticamente: {fuid.numero_fuid}")
            
            # 4. CONSTRUIR RESPUESTA COMBINADA (lo original + FUID)
            respuesta_combinada = {
                # === RESPUESTA ORIGINAL (lo que ya funcionaba) ===
                "status": "ok",
                "mensaje": "Documento registrado",
                "documento": {
                    "id": fuid.id,  # Usar el ID del FUID o mantener otro contador si prefieres
                    "nombre": resultado_ia["nombre_archivo"],
                    "extension": resultado_ia["extension"],
                    "version": resultado_ia["version"],
                    "tamano_kb": resultado_ia["tamano_kb"],
                    "ruta_guardado": resultado_ia["ruta_guardado"],
                    "duplicado": False,  # O la lógica de duplicados que tenías
                    "creado_en": fuid.creado_en.isoformat() if fuid.creado_en else None
                },
                "metadatos_extra": {
                    k: v for k, v in resultado_ia.items() 
                    if k not in ("nombre_archivo", "extension", "version", "hash_archivo", "ruta_guardado", "tamano_kb", "usuario_id")
                },
                
                # === INFORMACIÓN NUEVA DEL FUID ===
                "fuid_generado": {
                    "numero_fuid": fuid.numero_fuid,
                    "id_fuid": fuid.id,
                    "hash_fuid": fuid.hash_fuid,
                    "fecha_generacion": fuid.fecha_generacion.isoformat(),
                    "expediente_id": expediente_id
                },
                "procesado_automaticamente": True
            }
            
            # Añadir usuario_id a metadatos_extra si no está
            if "usuario_id" not in respuesta_combinada["metadatos_extra"]:
                respuesta_combinada["metadatos_extra"]["usuario_id"] = usuario_id
            
            return {
                "success": True,
                "respuesta": respuesta_combinada
            }
            
        except Exception as e:
            logger.error(f"Error en integración URL->FUID: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _enriquecer_metadata_fuid(self, metadata_ia: dict, url_original: str) -> dict:
        """
        Convierte la metadata básica de la IA al formato FUID extendido
        """
        return {
            # Metadata básica de la IA (original)
            "nombre_archivo": metadata_ia.get("nombre_archivo"),
            "extension": metadata_ia.get("extension"),
            "tamano_kb": metadata_ia.get("tamano_kb"),
            "hash_archivo": metadata_ia.get("hash_archivo"),
            "content_type": metadata_ia.get("content_type"),
            "last_modified": metadata_ia.get("last_modified"),
            "servidor": metadata_ia.get("servidor"),
            "usuario_id": metadata_ia.get("usuario_id"),
            
            # Metadata específica FUID (nueva)
            "url_origen": url_original,
            "procesado_por_ia": True,
            "soporte": "Electrónico",
            "cantidad_documentos": 1,
            "tipo_archivo": self._clasificar_tipo_archivo(metadata_ia.get("extension")),
            
            # Campos para análisis futuro de IA
            "series_subseries": "POR_CLASIFICAR",
            "nombre_unidad_documental": metadata_ia.get("nombre_archivo"),
            "fechas_extremas": {
                "inicial": "POR_DETECTAR",
                "final": "POR_DETECTAR"
            }
        }
    
    def _clasificar_tipo_archivo(self, extension: str) -> str:
        """Clasificación simple por extensión"""
        clasificacion = {
            "pdf": "Documento PDF",
            "docx": "Documento Word", 
            "xlsx": "Hoja de cálculo",
            "jpg": "Imagen",
            "png": "Imagen",
            "html": "Página web",
            "bin": "Archivo binario"
        }
        return clasificacion.get(extension.lower(), "Documento electrónico")