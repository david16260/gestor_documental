# test_xml_generation.py
"""
Script de prueba para validar la generación de XML
Ejecutar: python test_xml_generation.py
"""

from datetime import datetime
from app.services.xml_generator_service import (
    generar_xml_documento,
    determinar_tipologia,
    determinar_formato
)

# Clase mock para simular un documento
class DocumentoMock:
    def __init__(self):
        self.id = 1
        self.usuario_id = 2016555
        self.nombre_archivo = "Acto administrativo nombramiento.pdf"
        self.extension = "pdf"
        self.hash_archivo = "AXWQD1135210ABCDEF1234567890"
        self.tamano_kb = 527.0
        self.creado_en = datetime(2017, 7, 21)
        self.ruta_guardado = "/uploads/user_1/documento.pdf"

def test_generar_xml():
    """Prueba la generación de XML para un documento"""
    
    print("=" * 60)
    print("PRUEBA DE GENERACIÓN DE XML")
    print("=" * 60)
    
    # Crear documento de prueba
    doc = DocumentoMock()
    
    # Generar XML
    xml_output = generar_xml_documento(
        documento=doc,
        usuario_nombre="Juan Pérez",
        orden=1,
        pagina_inicio=1,
        pagina_fin=3
    )
    
    print("\nXML GENERADO:")
    print("-" * 60)
    print(xml_output)
    print("-" * 60)
    
    # Pruebas de funciones auxiliares
    print("\n\nPRUEBAS DE TIPOLOGÍA:")
    print("-" * 60)
    
    test_nombres = [
        "Acto administrativo nombramiento.pdf",
        "Comunicación oficial.docx",
        "Acta de reunión.pdf",
        "Contrato laboral.pdf",
        "Cédula de Ciudadanía.jpg",
        "Diploma bachiller.pdf",
        "Certificado de experiencia.pdf"
    ]
    
    for nombre in test_nombres:
        extension = nombre.split('.')[-1]
        tipologia = determinar_tipologia(nombre, extension)
        formato = determinar_formato(extension)
        print(f"Archivo: {nombre}")
        print(f"  → Tipología: {tipologia}")
        print(f"  → Formato: {formato}")
        print()

if __name__ == "__main__":
    test_generar_xml()