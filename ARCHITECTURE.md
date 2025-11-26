# Arquitectura y convenciones

- API FastAPI versionada en /api/v1 con routers por dominio: auth, documentos, TRD/CCD, ingesta, clasificación IA, expedientes/índices, FUID y adaptador SGDEA.
- Configuración por entorno vía .env (ver .env.example), centralizada en pp/core/config.py.
- Un único Base/engine/SessionLocal en pp/core/database.py para todos los modelos.
- Seguridad: JWT configurable y hashing bcrypt (pp/core/security.py), roles y protección OAuth2 Bearer.
- Subidas configurables (tamaño/extensiones) y segregadas por usuario (pp/api/documentos.py).
- Servicios: clasificación basada en reglas (pp/services/ia_classifier.py), generación XML y exportes SGDEA, ingesta desde Drive.
- Routers MVP: /trd, /ingesta, /clasificacion, /expedientes, /documentos, /fuid, /xml, /sgdea.
- Schemas Pydantic para contratos de salida (subidas, historial, índices, TRD, expedientes, clasificación) en pp/schemas/core.py.
- Pruebas iniciales y pipeline CI (	ests/test_smoke.py, .github/workflows/ci.yml).
- Contenerización lista (Dockerfile, docker-compose.yml).
- Pendiente: migraciones Alembic, pruebas de integración/E2E, contenedores por microservicio y stores especializados (ES/S3).
