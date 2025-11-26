# 📌 Gestor Documental con IA – Sprint 1

## 🎯 Objetivo del Sprint 1
Implementar la base del sistema de gestión documental en **Python + FastAPI**, asegurando que los usuarios puedan registrarse, crear sus carpetas locales, cargar documentos y que el sistema valide condiciones básicas (duplicidad e integridad).

---

## ✅ Historias de Usuario Cubiertas
- **HU1 – Registro de usuarios:**  
  Como usuario quiero registrarme para que el sistema me cree una carpeta personal donde almacenar mis documentos.  

- **HU2 – Carga de documentos:**  
  Como usuario quiero cargar documentos para que se guarden en mi carpeta personal.  

- **HU3 – Validación de duplicados:**  
  Como sistema quiero calcular hash de los archivos para detectar duplicados.  

- **HU4 – Validación de archivos vacíos:**  
  Como sistema quiero identificar si un archivo está vacío para notificar al usuario.  

---

## 🔨 Alcance Técnico (Sprint 1)
- Configuración del proyecto en **FastAPI** con estructura modular.  
- Creación del **entorno virtual (venv)** y gestión de dependencias en `requirements.txt`.  
- Endpoints iniciales:
  - `/users` → Registrar usuarios.  
  - `/upload` → Cargar documentos.  
  - Validaciones automáticas de duplicados y archivos vacíos.  
- Almacenamiento local organizado por carpetas de usuario.  

---

## 📅 Duración
- **Fecha de inicio:** 27 de septiembre de 2025  
- **Fecha de fin:** 11 de octubre de 2025  
- **Duración:** 2 semanas  

---

## 🛠️ Tecnologías
- Python 3.12  
- FastAPI  
- Uvicorn  
- Pydantic  
- Hashlib (para duplicados)  
- OS / pathlib (para manejo de archivos)  

---

## 📌 Criterios de Aceptación (DoD – Definition of Done)
- El sistema permite registrar un usuario y crear su carpeta automáticamente.  
- Se pueden cargar archivos y estos quedan organizados por usuario.  
- El sistema detecta duplicados correctamente usando hash.  
- El sistema detecta e informa cuando un archivo está vacío.  
- Documentación mínima en el README con instrucciones de uso.  

---

## 🚀 Ejecución del Proyecto
1. Activar entorno virtual:
   ```bash
   .\venv\Scripts\activate
   source venv/Scripts/activate
## Instalar dependencias:   
 pip install -r requirements.txt

## Instalar venv
python -m venv venv 

## Levantar servidor
uvicorn app.main:app --reload

## Salir del venv
deactivate


## Probar navegador
http://127.0.0.1:8000/docs

## Contenedores (Docker)
- Build: `docker build -t gestor-documental .`
- Levantar con base de datos: `docker-compose up --build`
- La API queda en `http://localhost:8000/api/v1`

## Arquitectura y cumplimiento (actualizado)
- API FastAPI versionada en `/api/v1` con routers por dominio: autenticación, documentos, TRD/CCD, ingesta, clasificación IA, expedientes/índices, FUID y adaptador SGDEA.
- Configuración centralizada con `.env` (`app/core/config.py`), un único `Base`/`engine`/`SessionLocal` (`app/core/database.py`) y CORS habilitado.
- Seguridad con JWT y hash bcrypt (`app/core/security.py`), roles y protección de rutas; endpoints de recuperación de contraseña.
- Modelos principales: usuarios, documentos, historial, TRD/CCD, expedientes, FUID; generación de XML e índices foliados.
- Servicios de IA y clasificación basada en reglas (`app/services/ia_classifier.py`), importación desde Drive y validación de TRD/CCD.
- Pruebas iniciales en `tests/test_smoke.py` y pipeline CI (`.github/workflows/ci.yml`).

