# main.py
from fastapi import FastAPI, Request
from app.database import engine, Base
from app.api import auth
from app.api import documentos
from app.api import documentos_versiones
from app.api import fuid 
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import documentos_url
from app.api import integration_router

# Crear todas las tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(title="Gestor Documental")

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
    """
    Página HTML para mostrar versiones.
    URL: /versiones
    """
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

# ===============================
# REGISTRAR ROUTERS
# ===============================
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(documentos.router, prefix="/documentos")        # Upload, historial
app.include_router(documentos_versiones.router)                    # Versiones API
app.include_router(fuid.router, prefix="/fuid", tags=["FUID"])    #fluid
app.include_router(integration_router.router, tags=["Integración IA-FUID"])  # integración IA-FUID

# ===============================
# Nota:
# - API JSON: /documentos/versiones -> devuelve las versiones
# - HTML: /versiones/html -> página con tabla de versiones
# ===============================
@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

app.include_router(documentos_url.router, prefix="/documentos")