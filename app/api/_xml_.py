from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.documento import Documento
from app.models.usuario import Usuario
from app.services.xml_generator_service import (
    generar_xml_documento,
    generar_xml_expediente_completo,
    guardar_xml_documento
)

router = APIRouter(prefix="/xml", tags=["XML Comprobantes"])


@router.get("/documento/{documento_id}")
def generar_xml_individual(documento_id: int, db: Session = Depends(get_db)):
    """
    Genera el XML de comprobante para un documento específico.
    """
    # Buscar documento
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == documento.usuario_id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Generar XML
    xml_content = generar_xml_documento(
        documento=documento,
        usuario_nombre=usuario.nombre,
        orden=1,
        pagina_inicio=1,
        pagina_fin=1
    )
    
    # Guardar XML
    xml_path = guardar_xml_documento(
        xml_string=xml_content,
        nombre_archivo=documento.nombre_archivo,
        usuario_id=documento.usuario_id
    )
    
    return {
        "mensaje": "XML generado exitosamente",
        "ruta_xml": xml_path,
        "xml_preview": xml_content
    }


@router.get("/documento/{documento_id}/descargar")
def descargar_xml_documento(documento_id: int, db: Session = Depends(get_db)):
    """
    Descarga el XML de comprobante de un documento.
    """
    # Buscar documento
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == documento.usuario_id).first()
    
    # Generar XML
    xml_content = generar_xml_documento(
        documento=documento,
        usuario_nombre=usuario.nombre if usuario else "Usuario",
        orden=1,
        pagina_inicio=1,
        pagina_fin=1
    )
    
    # Nombre del archivo para descarga
    nombre_sin_ext = documento.nombre_archivo.rsplit('.', 1)[0]
    filename = f"{nombre_sin_ext}_comprobante.xml"
    
    # Retornar como descarga
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/expediente/usuario/{usuario_id}")
def generar_xml_expediente_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Genera un XML completo con todos los documentos de un usuario (expediente).
    """
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Buscar todos los documentos del usuario
    documentos = db.query(Documento)\
        .filter(Documento.usuario_id == usuario_id)\
        .order_by(Documento.creado_en)\
        .all()
    
    if not documentos:
        raise HTTPException(status_code=404, detail="El usuario no tiene documentos")
    
    # Generar XML completo
    xml_content = generar_xml_expediente_completo(
        documentos=documentos,
        usuario_nombre=usuario.nombre,
        usuario_id=usuario_id
    )
    
    return {
        "mensaje": "XML de expediente generado exitosamente",
        "total_documentos": len(documentos),
        "xml_preview": xml_content
    }


@router.get("/expediente/usuario/{usuario_id}/descargar")
def descargar_xml_expediente(usuario_id: int, db: Session = Depends(get_db)):
    """
    Descarga el XML completo del expediente de un usuario.
    """
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Buscar documentos
    documentos = db.query(Documento)\
        .filter(Documento.usuario_id == usuario_id)\
        .order_by(Documento.creado_en)\
        .all()
    
    if not documentos:
        raise HTTPException(status_code=404, detail="El usuario no tiene documentos")
    
    # Generar XML
    xml_content = generar_xml_expediente_completo(
        documentos=documentos,
        usuario_nombre=usuario.nombre,
        usuario_id=usuario_id
    )
    
    filename = f"expediente_usuario_{usuario_id}_{usuario.nombre.replace(' ', '_')}.xml"
    
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/generar-automatico/{documento_id}")
def generar_xml_automatico_al_subir(documento_id: int, db: Session = Depends(get_db)):
    """
    Genera automáticamente el XML cuando se sube un documento.
    Este endpoint puede ser llamado desde el router de upload.
    """
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    usuario = db.query(Usuario).filter(Usuario.id == documento.usuario_id).first()
    
    # Generar XML
    xml_content = generar_xml_documento(
        documento=documento,
        usuario_nombre=usuario.nombre if usuario else "Usuario",
        orden=1,
        pagina_inicio=1,
        pagina_fin=1
    )
    
    # Guardar automáticamente
    xml_path = guardar_xml_documento(
        xml_string=xml_content,
        nombre_archivo=documento.nombre_archivo,
        usuario_id=documento.usuario_id
    )
    
    return {
        "mensaje": "XML generado automáticamente",
        "documento_id": documento_id,
        "ruta_xml": xml_path
    }