import json
from app import app

def test_listar_auditoria():
    """Prueba que la ruta /api/auditoria devuelva datos correctamente."""
    with app.test_client() as cliente:
        respuesta = cliente.get('/api/auditoria')
        assert respuesta.status_code == 200
        data = json.loads(respuesta.data)
        assert isinstance(data, list)
