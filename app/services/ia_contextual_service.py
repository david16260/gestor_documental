# app/services/ia_contextual_service.py
import os
import re
import PyPDF2
import docx
import numpy as np
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import logging

# Importaciones para IA contextual
import spacy
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class IAContextualService:
    def __init__(self):
        # Cargar modelos (solo una vez al iniciar)
        try:
            self.nlp = spacy.load("es_core_news_sm")
            self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.keybert_model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2')
            
            # Definir categorías con descripciones semánticas ricas
            self.categorias_contextuales = {
                "CONTRATOS_CLIENTES": {
                    "codigo": "100.03.01",
                    "area": "ADMINISTRATIVA", 
                    "serie": "CONTRATOS",
                    "subserie": "Contratos con clientes",
                    "descripciones_semanticas": [
                        "acuerdo de prestación de servicios con cliente",
                        "contrato de venta de productos o servicios",
                        "convenio comercial con comprador",
                        "documento de obligaciones con cliente",
                        "acuerdo de términos y condiciones de servicio"
                    ]
                },
                "CONTRATOS_PROVEEDORES": {
                    "codigo": "100.03.02",
                    "area": "ADMINISTRATIVA",
                    "serie": "CONTRATOS",
                    "subserie": "Contratos con proveedores", 
                    "descripciones_semanticas": [
                        "acuerdo de adquisición de suministros",
                        "contrato de compra con proveedor",
                        "convenio de abastecimiento",
                        "documento de obligaciones con suministrador",
                        "acuerdo de términos de compra"
                    ]
                },
                "ACTAS_ADMINISTRATIVAS": {
                    "codigo": "100.01.01",
                    "area": "ADMINISTRATIVA",
                    "serie": "ACTAS",
                    "subserie": "Administrativa",
                    "descripciones_semanticas": [
                        "registro de reunión de directivos",
                        "acta de sesión administrativa",
                        "minuta de reunión gerencial",
                        "resumen de decisiones directivas",
                        "memoria de sesión administrativa"
                    ]
                },
                "ACTAS_COMITE_ARCHIVO": {
                    "codigo": "100.01.02", 
                    "area": "ADMINISTRATIVA",
                    "serie": "ACTAS",
                    "subserie": "Comité de Archivo",
                    "descripciones_semanticas": [
                        "acta de comité de gestión documental",
                        "reunión sobre políticas de archivo",
                        "minuta de comité de documentos",
                        "registro de sesión sobre archivos",
                        "memoria de gestión documental"
                    ]
                },
                "INFORMES_GESTION": {
                    "codigo": "100.04",
                    "area": "ADMINISTRATIVA",
                    "serie": "INFORMES", 
                    "subserie": None,
                    "descripciones_semanticas": [
                        "informe de resultados y gestión",
                        "reporte de actividades realizadas",
                        "análisis de desempeño operativo",
                        "evaluación de gestión mensual",
                        "resumen ejecutivo de operaciones"
                    ]
                },
                "POLITICAS_INTERNAS": {
                    "codigo": "100.05",
                    "area": "ADMINISTRATIVA",
                    "serie": "POLITICAS",
                    "subserie": None,
                    "descripciones_semanticas": [
                        "política interna de la organización",
                        "normativa de procedimientos internos",
                        "reglamento de funcionamiento",
                        "directriz organizacional",
                        "protocolo de actuación interna"
                    ]
                },
                "COMPROBANTES_EGRESOS": {
    "codigo": "200.06.01",
    "area": "CONTABILIDAD", 
    "serie": "COMPROBANTES CONTABLES",
    "subserie": "Comprobantes Contables de Egresos",
    "descripciones_semanticas": [
        "documento de gastos y salidas de dinero",
        "comprobante de pago a proveedores",
        "factura de compra de bienes o servicios", 
        "egreso por conceptos operativos",
        "soporte de desembolso financiero",
        "documento de costo y gasto contable",
        "justificante de salida de fondos"
    ]
},
"COMPROBANTES_INGRESOS": {
    "codigo": "200.06.02",
    "area": "CONTABILIDAD",
    "serie": "COMPROBANTES CONTABLES",
    "subserie": "Comprobantes Contables de Ingresos", 
    "descripciones_semanticas": [
        "documento de entradas y recibos de dinero",
        "comprobante de ingreso por ventas",
        "factura de ingreso por servicios",
        "recibo de cobro a clientes",
        "soporte de entrada de fondos",
        "documento de revenue e ingresos",
        "justificante de percepción financiera"
    ]
},
"CONCILIACIONES_BANCARIAS": {
    "codigo": "200.07", 
    "area": "CONTABILIDAD",
    "serie": "CONCILIACIONES BANCARIAS",
    "subserie": None,
    "descripciones_semanticas": [
        "conciliación de cuenta bancaria",
        "comparación extracto bancario con libros",
        "ajuste de saldos contables con bancos",
        "documento de reconciliación financiera",
        "análisis de diferencias bancarias",
        "estado de conciliación monetaria",
        "reporte de ajuste contable bancario"
    ]
},
"DECLARACIONES_IMPUESTOS": {
    "codigo": "200.08",
    "area": "CONTABILIDAD",
    "serie": "DECLARACIONES DE IMPUESTOS", 
    "subserie": None,
    "descripciones_semanticas": [
        "declaración de impuestos ante autoridad",
        "formulario de obligaciones tributarias",
        "documento de impuesto sobre la renta",
        "declaración de IVA e impuestos",
        "reporte de retención en la fuente",
        "formulario de obligación fiscal",
        "declaración de impuestos nacionales"
    ]
},
"ESTADOS_FINANCIEROS": {
    "codigo": "200.09",
    "area": "CONTABILIDAD",
    "serie": "ESTADOS FINANCIEROS",
    "subserie": None,
    "descripciones_semanticas": [
        "estados financieros de la empresa", 
        "balance general y estado de resultados",
        "informe financiero contable",
        "estado de situación financiera",
        "reporte de resultados y patrimonio",
        "documento de posición financiera",
        "estados contables consolidados"
    ]
},
"INFORMES_EXOGENA": {
    "codigo": "200.10",
    "area": "CONTABILIDAD",
    "serie": "INFORMES EXOGENA",
    "subserie": None,
    "descripciones_semanticas": [
        "informe de información exógena",
        "reporte a entidades de control",
        "declaración de datos externos",
        "documento para autoridades fiscales", 
        "informe de cumplimiento regulatorio",
        "reporte exógeno de contabilidad",
        "declaración de información externa"
    ]
},
"LIBROS_DIARIOS": {
    "codigo": "200.11.01",
    "area": "CONTABILIDAD",
    "serie": "LIBROS CONTABLES PRINCIPALES",
    "subserie": "Libros Diarios",
    "descripciones_semanticas": [
        "libro diario de contabilidad",
        "registro cronológico de transacciones",
        "asientos contables diarios",
        "libro de movimientos financieros",
        "registro de operaciones contables",
        "documento de asientos del día",
        "libro de contabilidad general"
    ]
},
"LIBROS_MAYOR_BALANCE": {
    "codigo": "200.11.02", 
    "area": "CONTABILIDAD",
    "serie": "LIBROS CONTABLES PRINCIPALES",
    "subserie": "Libros Mayor y Balance",
    "descripciones_semanticas": [
        "libro mayor y balance de comprobación",
        "estado de cuentas contables",
        "balance de sumas y saldos",
        "libro de movimientos por cuenta",
        "documento de saldos contables",
        "registro de mayor general",
        "balance de comprobación contable"
    ]
},
"DOCUMENTOS_CONTABLES_GENERALES": {
    "codigo": "200.99",
    "area": "CONTABILIDAD", 
    "serie": "DOCUMENTOS CONTABLES",
    "subserie": None,
    "descripciones_semanticas": [
        "documento contable general",
        "registro financiero de operación",
        "comprobante contable variado",
        "documento de gestión financiera",
        "registro de operación económica",
        "documento de proceso contable",
        "registro de transacción financiera"
    ]
}
                
            }
            
            # Pre-calcular embeddings de categorías para mejor rendimiento
            self.embeddings_categorias = self._precalcular_embeddings_categorias()
            
            logger.info("Modelos de IA contextual cargados exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelos de IA: {str(e)}")
            raise

    def _precalcular_embeddings_categorias(self) -> Dict[str, np.ndarray]:
        """Pre-calcula embeddings para todas las descripciones semánticas"""
        embeddings = {}
        for categoria_id, info in self.categorias_contextuales.items():
            descripciones = info["descripciones_semanticas"]
            # Promedio de embeddings de todas las descripciones
            emb_descripciones = self.sentence_model.encode(descripciones)
            embeddings[categoria_id] = np.mean(emb_descripciones, axis=0)
        return embeddings

    def extraer_texto_archivo(self, ruta_archivo: str) -> str:
        """Extrae texto manteniendo estructura contextual"""
        try:
            extension = Path(ruta_archivo).suffix.lower()
            texto = ""
            
            if extension == '.pdf':
                with open(ruta_archivo, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        texto += page.extract_text() + "\n"
                        
            elif extension == '.docx':
                doc = docx.Document(ruta_archivo)
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        texto += paragraph.text + "\n"
                        
            elif extension in ['.txt']:
                with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as file:
                    texto = file.read()
                    
            return texto.strip()
            
        except Exception as e:
            logger.error(f"Error extrayendo texto de {ruta_archivo}: {str(e)}")
            return ""

    def analizar_estructura_contextual(self, texto: str) -> Dict[str, Any]:
        """Analiza la estructura y patrones del documento"""
        lineas = texto.split('\n')
        estructura = {
            "total_lineas": len(lineas),
            "lineas_no_vacias": len([l for l in lineas if l.strip()]),
            "patrones_detectados": [],
            "secciones_identificadas": []
        }
        
        # Detectar patrones estructurales comunes
        for i, linea in enumerate(lineas[:20]):  # Analizar primeras 20 líneas
            linea_upper = linea.upper().strip()
            
            # Detectar encabezados de actas
            if any(palabra in linea_upper for palabra in ['ACTA', 'REUNIÓN', 'SESION']):
                if 'Nº' in linea_upper or 'NUMERO' in linea_upper:
                    estructura["patrones_detectados"].append("encabezado_acta")
                    
            # Detectar encabezados de contratos
            if any(palabra in linea_upper for palabra in ['CONTRATO', 'CONVENIO', 'ACUERDO']):
                if any(palabra in linea_upper for palabra in ['ENTRE', 'CON', 'PARTES']):
                    estructura["patrones_detectados"].append("encabezado_contrato")
                    
            # Detectar informes
            if any(palabra in linea_upper for palabra in ['INFORME', 'REPORTE', 'ANALISIS']):
                estructura["patrones_detectados"].append("encabezado_informe")
                
            # Detectar políticas
            if any(palabra in linea_upper for palabra in ['POLITICA', 'PROCEDIMIENTO', 'NORMATIVA']):
                estructura["patrones_detectados"].append("encabezado_politica")
        
        return estructura

    def extraer_entidades_contextuales(self, texto: str) -> Dict[str, List[str]]:
        """Extrae entidades y sus relaciones contextuales"""
        doc = self.nlp(texto[:10000])  # Procesar primeros 10k caracteres para eficiencia
        
        entidades = {
            "organizaciones": [],
            "personas": [],
            "fechas": [],
            "montos": [],
            "ubicaciones": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entidades["organizaciones"].append(ent.text)
            elif ent.label_ == "PER":
                entidades["personas"].append(ent.text)
            elif ent.label_ == "DATE":
                entidades["fechas"].append(ent.text)
            elif ent.label_ == "MONEY":
                entidades["montos"].append(ent.text)
            elif ent.label_ == "LOC":
                entidades["ubicaciones"].append(ent.text)
        
        # Eliminar duplicados
        for key in entidades:
            entidades[key] = list(set(entidades[key]))
            
        return entidades

    def extraer_palabras_clave_contextuales(self, texto: str, n_keywords: int = 10) -> List[str]:
        """Extrae palabras clave que capturan el contexto semántico"""
        try:
            # Usar KeyBERT con MMR para diversidad semántica
            keywords = self.keybert_model.extract_keywords(
                texto,
                keyphrase_ngram_range=(1, 2),
                stop_words='spanish',
                use_mmr=True,
                diversity=0.7,
                top_n=n_keywords
            )
            return [kw[0] for kw in keywords if kw[1] > 0.2]  # Filtrar por relevancia
        except Exception as e:
            logger.warning(f"Error extrayendo keywords: {str(e)}")
            return []

    def analizar_contexto_completo(self, texto: str, nombre_archivo: str) -> Dict[str, Any]:
        """Análisis contextual completo del documento"""
        if not texto.strip():
            return self._clasificacion_por_defecto(nombre_archivo)
        
        # 1. Análisis estructural
        estructura = self.analizar_estructura_contextual(texto)
        
        # 2. Extracción de entidades
        entidades = self.extraer_entidades_contextuales(texto)
        
        # 3. Palabras clave contextuales
        palabras_clave = self.extraer_palabras_clave_contextuales(texto)
        
        # 4. Análisis semántico con embeddings
        embedding_documento = self.sentence_model.encode([texto])[0]
        
        # 5. Calcular similitudes semánticas con todas las categorías
        similitudes = {}
        for cat_id, emb_categoria in self.embeddings_categorias.items():
            similitud = cosine_similarity([embedding_documento], [emb_categoria])[0][0]
            similitudes[cat_id] = similitud
        
        # 6. Encontrar categoría con mayor similitud semántica
        categoria_id = max(similitudes.items(), key=lambda x: x[1])[0]
        confianza = similitudes[categoria_id]
        
        info_categoria = self.categorias_contextuales[categoria_id]
        
        # 7. Determinar unidad documental (empresa/cliente)
        unidad_documental = self._determinar_unidad_documental(entidades, palabras_clave, nombre_archivo)
        
        return {
            "clasificacion_principal": {
                "area": info_categoria["area"],
                "serie": info_categoria["serie"],
                "subserie": info_categoria["subserie"],
                "codigo": info_categoria["codigo"],
                "confianza": float(confianza)
            },
            "analisis_contextual": {
                "estructura": estructura,
                "entidades": entidades,
                "palabras_clave_contextuales": palabras_clave,
                "similitudes_categorias": {k: float(v) for k, v in similitudes.items()}
            },
            "unidad_documental": unidad_documental,
            "metadatos_contexto": {
                "total_palabras": len(texto.split()),
                "entidades_identificadas": sum(len(v) for v in entidades.values()),
                "categoria_principal": categoria_id
            }
        }

    def _determinar_unidad_documental(self, entidades: Dict, palabras_clave: List[str], nombre_archivo: str) -> str:
        """Determina la empresa/cliente principal basado en contexto"""
        # Priorizar organizaciones encontradas
        if entidades["organizaciones"]:
            # Buscar la organización más probable (no la propia empresa)
            organizaciones = entidades["organizaciones"]
            empresas_propias = ["MIEMPRESA", "EMPRESA", "COMPAÑÍA", "CORPORACIÓN"]
            
            for org in organizaciones:
                org_upper = org.upper()
                if not any(propia in org_upper for propia in empresas_propias):
                    if len(org) > 5:  # Evitar nombres muy cortos
                        return org
        
        # Buscar en palabras clave
        for keyword in palabras_clave:
            keyword_upper = keyword.upper()
            if any(palabra in keyword_upper for palabra in ['S.A.', 'LTDA', 'INC', 'CORP']):
                return keyword
        
        # Buscar en nombre de archivo
        nombre_upper = nombre_archivo.upper()
        empresas_conocidas = ['ALQUERÍA', 'EMPRENDU', 'TECHNOLOGY', 'SOLUTIONS', 'INNOVATION']
        
        for empresa in empresas_conocidas:
            if empresa in nombre_upper:
                return empresa
        
        return "Entidad No Identificada"

    def _clasificacion_por_defecto(self, nombre_archivo: str) -> Dict[str, Any]:
        """Clasificación por defecto cuando no hay texto suficiente"""
        return {
            "clasificacion_principal": {
                "area": "ADMINISTRATIVA",
                "serie": "DOCUMENTOS GENERALES", 
                "subserie": None,
                "codigo": "100.99",
                "confianza": 0.1
            },
            "analisis_contextual": {
                "estructura": {"total_lineas": 0, "lineas_no_vacias": 0, "patrones_detectados": []},
                "entidades": {"organizaciones": [], "personas": [], "fechas": [], "montos": [], "ubicaciones": []},
                "palabras_clave_contextuales": [],
                "similitudes_categorias": {}
            },
            "unidad_documental": "Documento General",
            "metadatos_contexto": {
                "total_palabras": 0,
                "entidades_identificadas": 0,
                "categoria_principal": "GENERAL"
            }
        }

    def clasificar_documento_contextual(self, ruta_archivo: str, nombre_archivo: str) -> Dict[str, Any]:
        """Clasificación principal que usa comprensión contextual completa"""
        try:
            # Extraer texto
            texto = self.extraer_texto_archivo(ruta_archivo)
            
            # Análisis contextual completo
            resultado = self.analizar_contexto_completo(texto, nombre_archivo)
            
            logger.info(f"Documento {nombre_archivo} clasificado con confianza: {resultado['clasificacion_principal']['confianza']:.2f}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error en clasificación contextual de {nombre_archivo}: {str(e)}")
            return self._clasificacion_por_defecto(nombre_archivo)