# main.py (actualizado)
from fastapi import FastAPI, Request
from app.database import engine, Base
from app.api import auth
from app.api import documentos
from app.api import documentos_versiones
from app.api import fuid 
from app.api import auditoria  # <-- NUEVO IMPORT
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import documentos_url
from app.api import integration_router
from app.core.config import settings

# Importar el router XML desde el archivo correcto
from app.api.xml_router import router as xml_router

# Crear todas las tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Gestor Documental - SGDEA",
    description="Sistema de Gestión Documental Electrónica de Archivo con APIs REST y GraphQL",
    version="2.0.0"
)

# Montar directorio estático
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar plantillas
templates = Jinja2Templates(directory="app/templates")

# ===============================
# ENDPOINTS HTML
# ===============================
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "titulo": "Iniciar sesión | Gestor Documental"
    })

@app.get("/register", response_class=HTMLResponse)
async def mostrar_registro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "titulo": "Panel | Gestor Documental"})

@app.get("/documentos", response_class=HTMLResponse)
async def subir_documento(request: Request):
    return templates.TemplateResponse("documentos.html", {"request": request, "titulo": "Subir Documento | Gestor Documental"})

@app.get("/versiones", response_class=HTMLResponse)
async def versiones_vigentes_html(request: Request):
    return templates.TemplateResponse("versiones.html", {
        "request": request,
        "titulo": "Versiones Vigentes | Gestor Documental"
    })

@app.get("/historial", response_class=HTMLResponse)
async def historial_page(request: Request):
    return templates.TemplateResponse("historial.html", {
        "request": request,
        "titulo": "Historial Documento | Gestor Documental"
    })

@app.get("/sgdea", response_class=HTMLResponse)
async def sgdea_dashboard(request: Request):
    return templates.TemplateResponse("sgdea_dashboard.html", {
        "request": request,
        "titulo": "SGDEA - Gestión Documental Electrónica"
    })

# NUEVA PÁGINA DE AUDITORÍA
@app.get("/auditoria", response_class=HTMLResponse)
async def pagina_auditoria(request: Request):
    return templates.TemplateResponse("auditoria.html", {
        "request": request,
        "titulo": "Auditoría | Gestor Documental"
    })

# ===============================
# REGISTRAR ROUTERS
# ===============================

# APIs existentes
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(documentos.router, prefix="/documentos", tags=["Documentos"])
app.include_router(documentos_versiones.router, tags=["Versiones"])
app.include_router(fuid.router, prefix="/fuid", tags=["FUID"])
app.include_router(integration_router.router, tags=["Integración IA-FUID"])
app.include_router(documentos_url.router, prefix="/documentos", tags=["Documentos URL"])
app.include_router(auditoria.router, prefix="/api", tags=["Auditoría"])  # <-- NUEVO ROUTER

# ===============================
# NUEVO ROUTER XML
# ===============================
app.include_router(xml_router, prefix="/xml", tags=["XML Comprobantes"])

# ===============================
# APIs SGDEA - NUEVAS
# ===============================
app.include_router(
    documentos.sgdea_router, 
    prefix="/api/v1/sgdea", 
    tags=["SGDEA - APIs"]
)

# ===============================
# ENDPOINTS DE INFORMACIÓN DEL SISTEMA
# ===============================
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Gestor Documental SGDEA",
        "version": "2.0.0"
    }

@app.get("/api/info")
async def system_info():
    return {
        "system": "Gestor Documental - SGDEA",
        "version": "2.0.0",
        "apis_available": {
            "sgdea": {
                "documentos": "/api/v1/sgdea/sgdea/",
                "expedientes": "/api/v1/sgdea/sgdea/expedientes/", 
                "inventarios": "/api/v1/sgdea/sgdea/inventarios/",
                "exportacion": "/api/v1/sgdea/sgdea/inventarios/exportar/{id}"
            },
            "documentos": "/documentos",
            "autenticacion": "/auth",
            "versiones": "/versiones",
            "fuid": "/fuid",
            "integracion_ia": "/integracion",
            "xml": "/xml",
            "auditoria": "/api/auditoria"  # <-- NUEVA API
        }
    }

# ===============================
# PÁGINAS ADICIONALES
# ===============================
@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})