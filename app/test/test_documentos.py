import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_file():
    # Prueba con un archivo válido (ajusta con un archivo de test)
    response = client.post("/api/upload", files={"file": ("test.xml", b"<document><title>Test</title><content>Content</content></document>")})
    assert response.status_code == 200
    assert "filename" in response.json()

def test_invalid_xml():
    # Prueba con XML inválido
    response = client.post("/api/upload", files={"file": ("invalid.xml", b"<document><title>Test</title></document>")})
    assert response.status_code == 400