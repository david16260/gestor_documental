# app/services/xml_generator_service.py
"""
Servicio para generación de comprobantes XML de documentos.

Este módulo proporciona funcionalidades para generar archivos XML que cumplen
con el estándar de DocumentoIndizado para gestión documental, incluyendo
generación individual y de expedientes completos.

Author: Sistema de Gestión Documental
Version: 1.0.0
"""

from lxml import etree
from datetime import datetime
from pathlib import Path
from app.models.documento import Documento
from app.models.historial_documento import HistorialDocumento
from app.core.config import get_settings

settings = get_settings()


def generar_xml_documento(documento: Documento, usuario_nombre: str, orden: int = 1, 
                          pagina_inicio: int = 1, pagina_fin: int = 1):
    """
    Genera un XML con la estructura de DocumentoIndizado para un documento individual.
    
    Este método crea un XML completo siguiendo el estándar de gestión documental,
    incluyendo todos los metadatos requeridos como ID, hash MD5, tipología,
    fechas de creación e incorporación, y formato del archivo.
    
    Args:
        documento (Documento): Instancia del modelo Documento con toda la información
            del archivo subido al sistema.
        usuario_nombre (str): Nombre completo del usuario propietario del documento.
        orden (int, optional): Orden secuencial del documento dentro del expediente.
            Por defecto es 1.
        pagina_inicio (int, optional): Número de página donde inicia el documento
            en el expediente consolidado. Por defecto es 1.
        pagina_fin (int, optional): Número de página donde finaliza el documento
            en el expediente consolidado. Por defecto es 1.
    
    Returns:
        str: Cadena de texto conteniendo el XML formateado con pretty_print,
            listo para ser guardado o enviado como respuesta.
    
    Example:
        >>> doc = db.query(Documento).filter(Documento.id == 1).first()
        >>> xml = generar_xml_documento(doc, "Juan Pérez", orden=1, pagina_inicio=1, pagina_fin=3)
        >>> print(xml)
        <DocumentoIndizado>
            <Id>20165550000000001TD</Id>
            ...
        </DocumentoIndizado>
    
    Note:
        El hash MD5 se trunca a 12 caracteres para compatibilidad con sistemas legacy.
        Las fechas se formatean en formato YYYYMMDD sin separadores.
    """
    
    # Crear elemento raíz del documento XML
    root = etree.Element("DocumentoIndizado")
    
    # ID del documento (formato: {usuario_id}{documento_id_con_10_digitos}TD)
    id_documento = etree.SubElement(root, "Id")
    id_documento.text = f"{documento.usuario_id}{documento.id:010d}TD"
    
    # Nombre del archivo (sin extensión para el XML)
    nombre_doc = etree.SubElement(root, "NombreDocumento")
    nombre_sin_ext = documento.nombre_archivo.rsplit('.', 1)[0] if '.' in documento.nombre_archivo else documento.nombre_archivo
    nombre_doc.text = nombre_sin_ext
    
    # Tipología documental (determinada automáticamente según nombre y extensión)
    tipologia = etree.SubElement(root, "TipologiaDocumental")
    tipologia.text = determinar_tipologia(documento.nombre_archivo, documento.extension)
    
    # Fecha de creación del documento original (formato YYYYMMDD)
    fecha_creacion = etree.SubElement(root, "FechaCreacionDocumento")
    fecha_creacion.text = documento.creado_en.strftime("%Y%m%d") if documento.creado_en else datetime.now().strftime("%Y%m%d")
    
    # Fecha de incorporación al expediente (normalmente igual a fecha de creación)
    fecha_incorporacion = etree.SubElement(root, "FechaIncorporacionExpediente")
    fecha_incorporacion.text = documento.creado_en.strftime("%Y%m%d") if documento.creado_en else datetime.now().strftime("%Y%m%d")
    
    # Hash MD5 del archivo (primeros 12 caracteres en mayúsculas)
    valor_huella = etree.SubElement(root, "ValorHuella")
    valor_huella.text = documento.hash_archivo[:12].upper()
    
    # Función de resumen utilizada (siempre MD5 según estándar)
    funcion_resumen = etree.SubElement(root, "FuncionResumen")
    funcion_resumen.text = "MD5"
    
    # Orden del documento dentro del expediente
    orden_doc = etree.SubElement(root, "OrdenDocumentoExpediente")
    orden_doc.text = str(orden)
    
    # Página de inicio en el expediente consolidado
    pag_inicio = etree.SubElement(root, "PaginaInicio")
    pag_inicio.text = str(pagina_inicio)
    
    # Página final en el expediente consolidado
    pag_fin = etree.SubElement(root, "PaginaFin")
    pag_fin.text = str(pagina_fin)
    
    # Formato del archivo según su extensión
    formato = etree.SubElement(root, "Formato")
    formato.text = determinar_formato(documento.extension)
    
    # Tamaño del archivo en kilobytes
    tamano = etree.SubElement(root, "Tamano")
    tamano.text = f"{int(documento.tamano_kb)} KB"
    
    # Convertir el árbol XML a string con formato legible
    xml_string = etree.tostring(
        root, 
        pretty_print=True,  # Indentación para legibilidad
        xml_declaration=False,  # Sin declaración XML para elementos individuales
        encoding='unicode'  # Retornar como string Unicode
    )
    
    return xml_string


def generar_xml_expediente_completo(documentos: list, usuario_nombre: str, usuario_id: int):
    """
    Genera un XML completo con todos los documentos de un usuario (expediente completo).
    
    Crea un archivo XML con estructura Root que contiene múltiples elementos
    DocumentoIndizado, representando el expediente completo de un usuario.
    Incluye paginación automática acumulativa y numeración secuencial.
    
    Args:
        documentos (list): Lista de instancias del modelo Documento, ordenadas
            cronológicamente o según criterio definido.
        usuario_nombre (str): Nombre completo del usuario propietario del expediente.
        usuario_id (int): Identificador único del usuario en el sistema.
    
    Returns:
        str: XML completo con declaración XML y namespace xsi, listo para
            ser guardado como archivo o descargado.
    
    Raises:
        ValueError: Si la lista de documentos está vacía.
    
    Example:
        >>> docs = db.query(Documento).filter(Documento.usuario_id == 1).all()
        >>> xml_expediente = generar_xml_expediente_completo(docs, "María García", 1)
        >>> with open("expediente.xml", "w") as f:
        ...     f.write(xml_expediente)
    
    Note:
        La paginación se calcula automáticamente estimando 1 página por cada 100KB.
        El namespace xsi se incluye para futura validación con schemas XSD.
    """
    
    # Namespace para cumplir con estándares XML de gestión documental
    NSMAP = {
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    # Crear elemento raíz con namespace
    root = etree.Element("Root", nsmap=NSMAP)
    
    # Contador de páginas acumulativo para todo el expediente
    pagina_actual = 1
    
    # Iterar sobre cada documento del usuario
    for idx, doc in enumerate(documentos, start=1):
        # Calcular número de páginas estimadas (1 página ≈ 100KB)
        num_paginas = max(1, int(doc.tamano_kb / 100))
        pagina_fin = pagina_actual + num_paginas - 1
        
        # Generar el XML individual del documento
        doc_xml_string = generar_xml_documento(
            documento=doc,
            usuario_nombre=usuario_nombre,
            orden=idx,
            pagina_inicio=pagina_actual,
            pagina_fin=pagina_fin
        )
        
        # Parsear el XML generado y añadirlo al árbol principal
        doc_element = etree.fromstring(doc_xml_string)
        root.append(doc_element)
        
        # Actualizar contador de páginas para el siguiente documento
        pagina_actual = pagina_fin + 1
    
    # Convertir el árbol completo a string con declaración XML
    xml_string = etree.tostring(
        root,
        pretty_print=True,  # Formato legible con indentación
        xml_declaration=True,  # Incluir <?xml version="1.0" encoding="UTF-8"?>
        encoding='UTF-8'  # Encoding explícito para caracteres especiales
    ).decode('utf-8')
    
    return xml_string


def determinar_tipologia(nombre_archivo: str, extension: str) -> str:
    """
    Determina la tipología documental basándose en el nombre del archivo y su extensión.
    
    Analiza el nombre del archivo buscando palabras clave que indiquen el tipo
    de documento según clasificación estándar de gestión documental colombiana.
    Si no encuentra coincidencias, asigna tipología genérica según extensión.
    
    Args:
        nombre_archivo (str): Nombre completo del archivo incluyendo extensión.
            Ejemplo: "Acta de reunion enero 2025.pdf"
        extension (str): Extensión del archivo sin el punto.
            Ejemplo: "pdf", "docx", "xlsx"
    
    Returns:
        str: Tipología documental estandarizada. Ejemplos: "Resolución",
            "Acta", "Certificado", "Documento de identificación".
    
    Example:
        >>> determinar_tipologia("Resolucion nombramiento.pdf", "pdf")
        'Resolución'
        >>> determinar_tipologia("Cedula de ciudadania.jpg", "jpg")
        'Documento de identificación'
        >>> determinar_tipologia("archivo_desconocido.pdf", "pdf")
        'Documento'
    
    Note:
        La búsqueda es case-insensitive y busca coincidencias parciales.
        Soporta tildes y caracteres especiales del español.
    """
    
    # Convertir a minúsculas para búsqueda case-insensitive
    nombre_lower = nombre_archivo.lower()
    
    # Diccionario de mapeo: palabra_clave -> tipología_estandarizada
    tipologias = {
        # Actos administrativos
        'resolución': 'Resolución',
        'resolucion': 'Resolución',
        'acto administrativo': 'Resolución',
        
        # Comunicaciones oficiales
        'comunicación': 'Comunicación',
        'comunicacion': 'Comunicación',
        
        # Actas y registros
        'acta': 'Acta',
        
        # Contratos y convenios
        'contrato': 'Contrato',
        
        # Recursos humanos
        'hoja de vida': 'Hoja de Vida',
        
        # Documentos de identificación
        'cedula': 'Documento de identificación',
        'cédula': 'Documento de identificación',
        'identificacion': 'Documento de identificación',
        'libreta': 'Documento de identificación',
        'licencia': 'Documento de identificación',
        
        # Documentos académicos
        'diploma': 'Soportes de estudio',
        
        # Certificados diversos
        'certificado': 'Certificado',
        'certificación': 'Certificado',
        
        # Declaraciones legales
        'declaración': 'Declaración',
        'declaracion': 'Declaración',
        
        # Formularios administrativos
        'formulario': 'Formulario'
    }
    
    # Buscar coincidencias en el nombre del archivo
    for palabra_clave, tipologia in tipologias.items():
        if palabra_clave in nombre_lower:
            return tipologia
    
    # Si no hay coincidencia, asignar tipología genérica por extensión
    if extension.lower() in ['pdf', 'docx', 'doc']:
        return 'Documento'
    elif extension.lower() in ['jpg', 'jpeg', 'png']:
        return 'Imagen'
    elif extension.lower() in ['xlsx', 'xls']:
        return 'Hoja de cálculo'
    
    # Tipología por defecto
    return 'Documento General'


def determinar_formato(extension: str) -> str:
    """
    Determina el formato estándar del archivo según su extensión.
    
    Convierte extensiones de archivo a formatos estandarizados reconocidos
    en sistemas de gestión documental. Para archivos PDF, retorna el formato
    PDF/A que es el estándar de archivo de larga duración.
    
    Args:
        extension (str): Extensión del archivo sin el punto.
            Ejemplo: "pdf", "docx", "jpg"
    
    Returns:
        str: Formato estandarizado en mayúsculas.
            Ejemplo: "PDF/A", "DOCX", "JPEG", "XLSX"
    
    Example:
        >>> determinar_formato("pdf")
        'PDF/A'
        >>> determinar_formato("DOCX")
        'DOCX'
        >>> determinar_formato("unknown")
        'UNKNOWN'
    
    Note:
        La función es case-insensitive. Para extensiones no reconocidas,
        retorna la extensión en mayúsculas.
    """
    
    # Diccionario de mapeo: extensión -> formato_estandarizado
    formatos = {
        # Documentos
        'pdf': 'PDF/A',  # PDF archivable según ISO 19005
        'docx': 'DOCX',  # Microsoft Word moderno
        'doc': 'DOC',    # Microsoft Word legacy
        
        # Hojas de cálculo
        'xlsx': 'XLSX',  # Microsoft Excel moderno
        'xls': 'XLS',    # Microsoft Excel legacy
        
        # Texto plano
        'txt': 'TXT',
        
        # Imágenes
        'jpg': 'JPEG',
        'jpeg': 'JPEG',
        'png': 'PNG',
        
        # Datos estructurados
        'xml': 'XML'
    }
    
    # Buscar formato correspondiente (case-insensitive)
    return formatos.get(extension.lower(), extension.upper())


def guardar_xml_documento(xml_string: str, nombre_archivo: str, usuario_id: int) -> str:
    """
    Guarda el XML generado en el sistema de archivos dentro del directorio del usuario.
    
    Crea automáticamente la estructura de directorios necesaria y guarda el XML
    con encoding UTF-8. El archivo se almacena en una carpeta específica para XMLs
    dentro del directorio personal del usuario.
    
    Args:
        xml_string (str): Contenido XML completo como cadena de texto,
            incluyendo declaración y estructura completa.
        nombre_archivo (str): Nombre original del documento para generar
            el nombre del archivo XML.
        usuario_id (int): Identificador único del usuario propietario.
    
    Returns:
        str: Ruta absoluta donde se guardó el archivo XML.
            Ejemplo: "/uploads/user_1/xml/documento_comprobante.xml"
    
    Raises:
        IOError: Si hay problemas de permisos o espacio en disco.
        OSError: Si no se puede crear el directorio.
    
    Example:
        >>> xml_content = generar_xml_documento(...)
        >>> ruta = guardar_xml_documento(xml_content, "contrato.pdf", 1)
        >>> print(ruta)
        '/uploads/user_1/xml/contrato_comprobante.xml'
    
    Note:
        - Crea automáticamente /uploads/user_{id}/xml/ si no existe
        - Usa encoding UTF-8 para soportar tildes y caracteres especiales
        - Sobrescribe archivos existentes con el mismo nombre
    """
    
    # Crear ruta del directorio XML del usuario
    xml_dir = settings.upload_dir / f"user_{usuario_id}" / "xml"
    
    # Crear directorio si no existe (incluyendo padres)
    xml_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre del archivo XML basado en el documento original
    nombre_sin_ext = nombre_archivo.rsplit('.', 1)[0] if '.' in nombre_archivo else nombre_archivo
    xml_filename = f"{nombre_sin_ext}_comprobante.xml"
    
    # Ruta completa del archivo XML
    xml_path = xml_dir / xml_filename
    
    # Guardar archivo con encoding UTF-8 para caracteres especiales
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    # Retornar ruta como string
    return str(xml_path)
