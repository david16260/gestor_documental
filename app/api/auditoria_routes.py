from flask import Blueprint, jsonify
from app.controllers.auditoria_controller import obtener_auditoria

auditoria_bp = Blueprint('auditoria', __name__)

@auditoria_bp.route('/api/auditoria', methods=['GET'])
def listar_auditoria():
    """Lista todos los registros de auditoría."""
    registros = obtener_auditoria()
    data = [
        {
            'id': r.id,
            'usuario': r.usuario,
            'accion': r.accion,
            'entidad': r.entidad,
            'detalle': r.detalle,
            'fecha_hora': r.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        }
        for r in registros
    ]
    return jsonify(data), 200
