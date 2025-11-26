from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.core.database import Base, engine
from app.api import auth, documentos, documentos_versiones, documentos_url
from app.api.fuid_corregido import router as fuid_router
from app.api.xml_routes import router as xml_router
from app.api import trd_ccd, expedientes, clasificacion, ingesta

app = FastAPI(title=settings.app_name, debug=settings.debug)
api_v1 = APIRouter(prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
# ROUTERS PRINCIPALES (API v1)
# ===============================
api_v1.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_v1.include_router(documentos.router, prefix="/documentos", tags=["Documentos"])
api_v1.include_router(documentos_versiones.router, tags=["Versiones"])
api_v1.include_router(documentos_url.router, prefix="/documentos", tags=["Documentos URL"])
api_v1.include_router(fuid_router, prefix="/fuid", tags=["FUID"])
api_v1.include_router(xml_router, tags=["XML Comprobantes"])
api_v1.include_router(documentos.sgdea_router, prefix="/sgdea", tags=["SGDEA"])
api_v1.include_router(trd_ccd.router)
api_v1.include_router(expedientes.router)
api_v1.include_router(clasificacion.router)
api_v1.include_router(ingesta.router)

app.include_router(api_v1)


# ===============================
# ENDPOINTS AUXILIARES
# ===============================
@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})


# Crear tablas
Base.metadata.create_all(bind=engine)
