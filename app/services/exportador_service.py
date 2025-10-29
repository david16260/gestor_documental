# app/services/exportador_service.py
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from fastapi.responses import Response
from app.schemas.sgdea import FormatoInventario

class ExportadorService:
    @staticmethod
    def exportar_json(data: dict, filename: str = "exportacion") -> Response:
        """Exportar datos en formato JSON"""
        json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}.json"}
        )
    
    @staticmethod
    def exportar_xml(data: dict, root_element: str = "sgdea", filename: str = "exportacion") -> Response:
        """Exportar datos en formato XML"""
        root = ET.Element(root_element)
        
        def dict_to_xml(parent, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    child = ET.SubElement(parent, key)
                    dict_to_xml(child, value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            child = ET.SubElement(parent, key)
                            dict_to_xml(child, item)
                        else:
                            ET.SubElement(parent, key).text = str(item)
                else:
                    ET.SubElement(parent, key).text = str(value)
        
        dict_to_xml(root, data)
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        return Response(
            content=xml_str,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={filename}.xml"}
        )
    
    @staticmethod
    def exportar_inventario(inventario_data: dict, formato: FormatoInventario, filename: str = "inventario"):
        """Exportar inventario en el formato especificado"""
        if formato == FormatoInventario.JSON:
            return ExportadorService.exportar_json(inventario_data, filename)
        elif formato == FormatoInventario.XML:
            return ExportadorService.exportar_xml(inventario_data, "inventario", filename)
        else:
            return ExportadorService.exportar_json(inventario_data, filename)