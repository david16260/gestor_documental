# main.py
from fastapi import FastAPI, Request
from app.database import engine, Base
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import auth, documentos, documentos_versiones, documentos_url
from app.api.fuid_corregido import router as fuid_router
from app.api.xml_routes import router as xml_router 

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestor Documental FUID")

# Configuración estática y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ===============================
# ENDPOINTS HTML PRINCIPALES
# ===============================
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def mostrar_registro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/documentos", response_class=HTMLResponse)
async def subir_documento(request: Request):
    return templates.TemplateResponse("documentos.html", {"request": request})

@app.get("/versiones", response_class=HTMLResponse)
async def versiones_vigentes_html(request: Request):
    return templates.TemplateResponse("versiones.html", {"request": request})

@app.get("/historial", response_class=HTMLResponse)
async def historial_page(request: Request):
    return templates.TemplateResponse("historial.html", {"request": request})

@app.get("/clasificacion", response_class=HTMLResponse)
async def clasificacion_page(request: Request):
    return templates.TemplateResponse("clasificacion.html", {"request": request})

@app.get("/fuid", response_class=HTMLResponse)
async def fuid_page(request: Request):
    return templates.TemplateResponse("fuid.html", {"request": request})

# ===============================
# ROUTERS PRINCIPALES
# ===============================
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(documentos.router, prefix="/documentos", tags=["Documentos"])
app.include_router(documentos_versiones.router, tags=["Versiones"])
app.include_router(documentos_url.router, prefix="/documentos", tags=["Documentos URL"])
app.include_router(fuid_router, prefix="/fuid", tags=["FUID"])
app.include_router(xml_router, tags=["XML Comprobantes"])  # ← SIN prefix, ya que el router ya tiene /xml

# ===============================
# ENDPOINTS AUXILIARES
# ===============================
@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})