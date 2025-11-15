# app/api/fuid_corregido.py (VERSIÓN CON RESPUESTAS UNIFICADAS)
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import tempfile
import os
from pathlib import Path
import hashlib
from app.database import get_db
from app.services.ia_contextual_service import IAContextualService
from app.models.documento import Documento
from app.models.fuid_models import ExpedienteFUID, FUID
from app.utils.fuid_generator import generate_fuid
from app.utils.hash_generator import generate_hash
from datetime import datetime
import shutil

router = APIRouter(tags=["FUID"])
logger = logging.getLogger(__name__)

class ProcesarURLRequest(BaseModel):
    url: str
    version: str = "1.0"

# ===============================
# ENDPOINT PARA URLs (CORREGIDO)
# ===============================
@router.post("/procesar-url")
async def procesar_url_fuid(
    request: ProcesarURLRequest,
    db: Session = Depends(get_db)
):
    """Procesa documentos desde URL/Google Drive con FUID - VERSIÓN CON RESPUESTAS UNIFICADAS"""
    try:
        from app.services.documentos_url_service import process_external_document
        
        logger.info(f"🌐 PROCESANDO URL FUID: {request.url}")
        
        # Descargar documentos usando tu servicio existente
        documentos_metadata = process_external_document(request.url, 1, request.version)
        
        if not documentos_metadata:
            raise HTTPException(status_code=400, detail="No se obtuvieron documentos de la URL")
        
        resultados = []
        expedientes_creados = {}
        
        for metadata in documentos_metadata:
            try:
                ruta_archivo = metadata["ruta_guardado"]
                nombre_archivo = metadata["nombre_archivo"]
                
                logger.info(f"📄 Procesando: {nombre_archivo}")
                
                # Procesar con IA contextual
                ia_service = IAContextualService()
                resultado_ia = ia_service.clasificar_documento_contextual(
                    ruta_archivo, 
                    nombre_archivo
                )
                
                clasificacion = resultado_ia["clasificacion_principal"]
                unidad_documental = resultado_ia.get("unidad_documental", "No identificada")
                codigo = clasificacion["codigo"]
                
                logger.info(f"✅ Clasificado: {nombre_archivo} -> {clasificacion['area']}/{clasificacion['serie']}")
                
                # Mover archivo físicamente a carpeta clasificada
                ruta_final = mover_archivo_a_carpeta_clasificada(
                    ruta_archivo, 
                    clasificacion, 
                    nombre_archivo
                )
                
                # Guardar documento en BD con la nueva ruta
                documento_db = Documento(
                    nombre_archivo=nombre_archivo,
                    ruta_guardado=ruta_final,
                    area=clasificacion["area"],
                    serie=clasificacion["serie"],
                    subserie=clasificacion["subserie"],
                    codigo_clasificacion=codigo,
                    confianza_clasificacion=clasificacion["confianza"],
                    palabras_clave_contextuales=", ".join(resultado_ia["analisis_contextual"]["palabras_clave_contextuales"]),
                    nombre_unidad_documental=unidad_documental,
                    usuario_id=1,
                    extension=metadata["extension"],
                    version=request.version,
                    tamano_kb=metadata["tamano_kb"],
                    hash_archivo=metadata["hash_archivo"]
                )
                
                db.add(documento_db)
                db.flush()
                
                # Agrupar por expediente
                if codigo not in expedientes_creados:
                    expediente = crear_o_obtener_expediente(db, clasificacion, unidad_documental, 1)
                    
                    if not expediente.id:
                        logger.error(f"❌ Expediente sin ID para código: {codigo}")
                        continue
                    
                    fuid = crear_fuid_para_expediente(db, expediente, 1)
                    expedientes_creados[codigo] = {
                        "expediente": expediente,
                        "fuid": fuid,
                        "documentos": []
                    }
                
                expedientes_creados[codigo]["documentos"].append(documento_db)
                expedientes_creados[codigo]["expediente"].cantidad_documentos += 1
                
                # RESULTADO UNIFICADO - TODOS LOS CAMPOS COMO STRING
                resultados.append({
                    "documento": str(nombre_archivo),
                    "clasificacion": f"{clasificacion['area']}/{clasificacion['serie']}",
                    "unidad_documental": str(unidad_documental),
                    "confianza": f"{clasificacion['confianza']:.2f}%",
                    "ruta_final": str(ruta_final)
                })
                
            except Exception as e:
                logger.error(f"❌ Error procesando {metadata.get('nombre_archivo', 'desconocido')}: {str(e)}")
                continue
        
        if not expedientes_creados:
            db.rollback()
            raise HTTPException(status_code=500, detail="No se pudieron crear expedientes FUID")
        
        # Actualizar tamaños de expedientes
        for codigo, data in expedientes_creados.items():
            total_size = sum(doc.tamano_kb for doc in data["documentos"]) / 1024
            data["expediente"].tamaño_documentos = f"{total_size:.2f}MB"
        
        db.commit()
        
        logger.info(f"✅ Procesamiento completado: {len(resultados)} documentos, {len(expedientes_creados)} expedientes")
        
        # RESPUESTA UNIFICADA - TODOS LOS DATOS COMO STRINGS
        expedientes_response = []
        for codigo, data in expedientes_creados.items():
            expedientes_response.append({
                "fuid": str(data["fuid"].numero_fuid),
                "codigo": str(codigo),
                "documentos": str(len(data["documentos"])),
                "unidad_documental": str(data["expediente"].nombre_unidad_documental)
            })
        
        return {
            "estado": "completado",
            "mensaje": f"Procesados {len(resultados)} documentos con FUID",
            "procesados": len(resultados),
            "expedientes_creados": expedientes_response,  # LISTA UNIFICADA
            "resultados": resultados  # LISTA UNIFICADA
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ ERROR FUID URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando URL: {str(e)}")

# ===============================
# ENDPOINT PARA ARCHIVOS LOCALES (CORREGIDO)
# ===============================
@router.post("/procesar-archivo")
async def procesar_archivo_fuid(
    file: UploadFile = File(...),
    version: str = Form("1.0"),
    db: Session = Depends(get_db)
):
    """Procesa un archivo individual con FUID e IA contextual - VERSIÓN CON RESPUESTAS UNIFICADAS"""
    try:
        logger.info(f"🚀 INICIANDO FUID para: {file.filename}")
        
        # Validar tipo de archivo
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Use: {', '.join(allowed_extensions)}"
            )

        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        ruta_final = tmp_path  # Inicializar para el bloque finally

        try:
            # Procesar con IA contextual
            ia_service = IAContextualService()
            resultado_ia = ia_service.clasificar_documento_contextual(
                tmp_path, 
                file.filename
            )
            
            clasificacion = resultado_ia["clasificacion_principal"]
            unidad_documental = resultado_ia.get("unidad_documental", "No identificada")
            
            # VERIFICAR DUPLICADOS
            hash_archivo = hashlib.md5(content).hexdigest()
            documento_existente = db.query(Documento).filter(
                Documento.hash_archivo == hash_archivo
            ).first()
            
            if documento_existente:
                logger.info(f"📄 Usando documento existente: {documento_existente.id}")
                documento_db = documento_existente
                ruta_final = documento_db.ruta_guardado
            else:
                # Mover archivo físicamente a carpeta clasificada
                ruta_final = mover_archivo_a_carpeta_clasificada(
                    tmp_path, 
                    clasificacion, 
                    file.filename
                )
                
                # Guardar documento en BD
                documento_db = Documento(
                    nombre_archivo=file.filename,
                    ruta_guardado=ruta_final,
                    area=clasificacion["area"],
                    serie=clasificacion["serie"],
                    subserie=clasificacion["subserie"],
                    codigo_clasificacion=clasificacion["codigo"],
                    confianza_clasificacion=clasificacion["confianza"],
                    palabras_clave_contextuales=", ".join(resultado_ia["analisis_contextual"]["palabras_clave_contextuales"]),
                    nombre_unidad_documental=unidad_documental,
                    usuario_id=1,
                    extension=file_extension,
                    version=version,
                    tamano_kb=os.path.getsize(ruta_final) / 1024,
                    hash_archivo=hash_archivo
                )
                db.add(documento_db)
            
            db.flush()
            
            # CREAR EXPEDIENTE FUID
            expediente = crear_o_obtener_expediente(db, clasificacion, unidad_documental, 1)
            
            # CREAR FUID
            fuid = crear_fuid_para_expediente(db, expediente, 1)
            
            # Actualizar expediente
            expediente.cantidad_documentos = db.query(Documento).filter(
                Documento.codigo_clasificacion == expediente.codigo
            ).count()
            
            tamaño_total = db.query(Documento.tamano_kb).filter(
                Documento.codigo_clasificacion == expediente.codigo
            ).scalar() or 0
            expediente.tamaño_documentos = f"{(tamaño_total / 1024):.2f}MB"
            
            db.commit()
            
            logger.info(f"✅ FUID CREADO: {fuid.numero_fuid}")
            
            # RESPUESTA UNIFICADA - TODOS LOS DATOS COMO STRINGS
            return {
                "estado": "completado",
                "fuid": str(fuid.numero_fuid),
                "expediente_id": str(expediente.id),
                "documento_id": str(documento_db.id),
                "clasificacion": f"{clasificacion['area']}/{clasificacion['serie']}",
                "unidad_documental": str(unidad_documental),
                "confianza": f"{clasificacion['confianza']:.2f}%",
                "ruta_final": str(ruta_final)
            }
            
        finally:
            # Limpiar archivo temporal SOLO si no fue movido
            if os.path.exists(tmp_path) and tmp_path != ruta_final:
                os.unlink(tmp_path)
                logger.info(f"🧹 Archivo temporal eliminado: {tmp_path}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ ERROR FUID: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en FUID: {str(e)}")

# ===============================
# FUNCIONES AUXILIARES (MANTENIDAS)
# ===============================
def mover_archivo_a_carpeta_clasificada(ruta_original: str, clasificacion: dict, nombre_archivo: str) -> str:
    """Mueve físicamente el archivo a la carpeta clasificada"""
    try:
        ruta_carpeta = os.path.join(
            "uploads",
            clasificacion["area"],
            clasificacion["serie"]
        )
        
        os.makedirs(ruta_carpeta, exist_ok=True)
        
        ruta_destino = os.path.join(ruta_carpeta, nombre_archivo)
        
        if ruta_original == ruta_destino:
            logger.info(f"📁 Archivo ya en ubicación correcta: {ruta_destino}")
            return ruta_destino
        
        if os.path.exists(ruta_original):
            shutil.move(ruta_original, ruta_destino)
            logger.info(f"📦 Archivo movido: {ruta_original} → {ruta_destino}")
            return ruta_destino
        else:
            logger.warning(f"⚠️ Archivo original no encontrado: {ruta_original}")
            return ruta_original
            
    except Exception as e:
        logger.error(f"❌ Error moviendo archivo: {str(e)}")
        return ruta_original

def crear_o_obtener_expediente(db: Session, clasificacion: dict, unidad_documental: str, usuario_id: int):
    """Obtiene un expediente existente o crea uno nuevo"""
    codigo = clasificacion["codigo"]
    
    expediente = db.query(ExpedienteFUID).filter(
        ExpedienteFUID.codigo == codigo,
        ExpedienteFUID.usuario_id == usuario_id
    ).first()
    
    if expediente:
        logger.info(f"✅ Expediente existente: {expediente.id}")
        return expediente
    
    fecha_actual = datetime.now()
    expediente = ExpedienteFUID(
        codigo=codigo,
        nombre_series=clasificacion["serie"],
        nombre_subseries=clasificacion.get("subserie"),
        nombre_unidad_documental=unidad_documental,
        fecha_inicial=fecha_actual,
        fecha_final=fecha_actual,
        electronico=True,
        ubicacion=f"uploads/{clasificacion['area']}/{clasificacion['serie']}",
        cantidad_documentos=0,
        tamaño_documentos="0MB",
        usuario_id=usuario_id
    )
    
    db.add(expediente)
    db.flush()
    logger.info(f"✅ Nuevo expediente creado con ID: {expediente.id}")
    
    return expediente

def crear_fuid_para_expediente(db: Session, expediente: ExpedienteFUID, usuario_id: int):
    """Crea un FUID para un expediente"""
    fuid_existente = db.query(FUID).filter(FUID.expediente_id == expediente.id).first()
    if fuid_existente:
        logger.info(f"✅ FUID existente: {fuid_existente.numero_fuid}")
        return fuid_existente
    
    metadatos_fuid = {
        "codigo": expediente.codigo,
        "nombre_series": expediente.nombre_series,
        "nombre_subseries": expediente.nombre_subseries,
        "nombre_unidad_documental": expediente.nombre_unidad_documental,
        "fecha_inicial": expediente.fecha_inicial.isoformat(),
        "fecha_final": expediente.fecha_final.isoformat(),
        "electronico": True,
        "ubicacion": expediente.ubicacion,
        "cantidad_documentos": expediente.cantidad_documentos,
        "tamaño_documentos": expediente.tamaño_documentos
    }
    
    numero_fuid = generate_fuid()
    hash_data = {
        "expediente_id": expediente.id,
        "usuario_id": usuario_id,
        "metadatos_fuid": metadatos_fuid,
        "timestamp": str(datetime.now().timestamp())
    }
    hash_fuid = generate_hash(hash_data)
    
    fuid = FUID(
        numero_fuid=numero_fuid,
        expediente_id=expediente.id,
        usuario_id=usuario_id,
        metadatos_fuid=metadatos_fuid,
        referencia_contenido=expediente.ubicacion,
        hash_fuid=hash_fuid
    )
    
    db.add(fuid)
    logger.info(f"✅ Nuevo FUID creado: {numero_fuid} para expediente {expediente.id}")
    
    return fuid