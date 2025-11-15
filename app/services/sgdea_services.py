# app/services/sgdea_services.py
from typing import List, Optional
from app.schemas.sgdea import Expediente, ExpedienteCreate, Inventario, InventarioCreate, FormatoInventario
import uuid
from datetime import datetime

# Servicios específicos para Expedientes e Inventarios SGDEA

# Datos mock - integrar con BD real después
expedientes_db = {}
inventarios_db = {}

class ExpedienteService:
    @staticmethod
    def obtener_expedientes(
        skip: int = 0, 
        limit: int = 100, 
        estado: Optional[str] = None
    ) -> List[Expediente]:
        """Obtener lista de expedientes con filtros"""
        expedientes = list(expedientes_db.values())
        if estado:
            expedientes = [e for e in expedientes if e.estado == estado]
        return expedientes[skip:skip + limit]
    
    @staticmethod
    def obtener_por_id(expediente_id: str) -> Optional[Expediente]:
        """Obtener un expediente por su ID"""
        return expedientes_db.get(expediente_id)
    
    @staticmethod
    def crear_expediente(expediente: ExpedienteCreate) -> Expediente:
        """Crear un nuevo expediente"""
        expediente_id = str(uuid.uuid4())
        now = datetime.now()
        
        nuevo_expediente = Expediente(
            id=expediente_id,
            fecha_apertura=now,
            **expediente.dict()
        )
        expedientes_db[expediente_id] = nuevo_expediente
        return nuevo_expediente

class InventarioService:
    @staticmethod
    def obtener_inventarios() -> List[Inventario]:
        """Obtener todos los inventarios"""
        return list(inventarios_db.values())
    
    @staticmethod
    def generar_inventario(nombre: str, descripcion: str = "", formato: FormatoInventario = FormatoInventario.JSON) -> Inventario:
        """Generar un nuevo inventario del sistema"""
        inventario_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Datos de ejemplo para el inventario
        elementos = [
            {"tipo": "expediente", "total": len(expedientes_db)},
            {"tipo": "documento_sgdea", "total": len(expedientes_db)}  # Aquí integrar con tu BD real después
        ]
        
        nuevo_inventario = Inventario(
            id=inventario_id,
            nombre=nombre,
            descripcion=descripcion,
            fecha_generacion=now,
            elementos=elementos,
            total_elementos=len(elementos),
            formato=formato
        )
        inventarios_db[inventario_id] = nuevo_inventario
        return nuevo_inventario