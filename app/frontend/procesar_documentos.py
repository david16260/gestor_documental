# app/frontend/procesar_documentos.py
import streamlit as st
import requests
import time
from io import BytesIO

API_BASE = "http://127.0.0.1:8000"

def procesar_documentos_page(cambiar_vista):
    """Pantalla para procesar documentos con diferentes servicios."""
    
    # --- Validar sesión ---
    if "token" not in st.session_state or not st.session_state.token:
        st.warning("🔒 No has iniciado sesión.")
        cambiar_vista("login")
        st.stop()

    usuario = st.session_state.get("usuario_nombre", "Desconocido")

    # --- Estilos visuales ---
    st.markdown("""
    <style>
        .stApp {
    background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    color: #000000 !important;
}
p, h1, h2, h3, h4, h5, h6, div, span {
    color: #000000 !important;
}
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #81db85 0%, #69bc6c 100%) !important;
    color: white !important;
    border: none !important;
}

div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #81db85 0%, #69bc6c 100%) !important;
    color: white !important;
    border: none !important;
}

        .header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(135deg, #2e7d32, #388e3c);
            color: white;
            padding: 14px 30px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 16px;
        }

        .container {
            background: #ffffff;
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin-top: 140px;
            max-width: 900px;
            border: 1px solid #c8e6c9;
            margin-left: auto;
            margin-right: auto;
            transition: all 0.4s ease-in-out;
        }

        .service-card {
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
        }

        .service-card:hover {
            border-color: #2e7d32;
            background-color: #f8f9fa;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .service-card.selected {
            border-color: #2e7d32;
            background-color: #e8f5e9;
        }

        .service-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            text-align: center;
        }

        .upload-area {
            border: 3px dashed #4caf50;
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            background: #f8f9fa;
            transition: all 0.3s;
            cursor: pointer;
            margin-bottom: 20px;
        }

        .upload-area:hover {
            background: #e8f5e9;
            border-color: #2e7d32;
        }

        .upload-area.dragover {
            background: #c8e6c9;
            border-color: #1b5e20;
        }

        .file-info {
            background: #f1f8e9;
            border: 2px solid #81c784;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }

        .progress-container {
            margin: 20px 0;
        }

        .result-success {
            background: #e8f5e9;
            border: 2px solid #4caf50;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }

        .result-error {
            background: #ffebee;
            border: 2px solid #f44336;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    st.markdown(f"""
    <div class="header">
        <div>👤 {usuario} | Procesar Documentos</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

    # --- CONTENIDO PRINCIPAL ---
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.title("📁 Gestor Documental - Procesar Documentos")

    # Inicializar estado de sesión para esta página
    if "selected_service" not in st.session_state:
        st.session_state.selected_service = None
    if "selected_file" not in st.session_state:
        st.session_state.selected_file = None
    if "upload_progress" not in st.session_state:
        st.session_state.upload_progress = 0

    # --- SELECCIÓN DE SERVICIO ---
    st.markdown("### 🔍 Procesamiento FUID con IA:")


    col1, = st.columns(1)
    with col1:
        # Servicio: FUID - Clasificación con IA
        is_selected = st.session_state.selected_service == "fuid"
        

    # --- SECCIÓN DE SERVICIOS FUID ---
    if st.session_state.selected_service == "fuid":
        st.markdown("---")
        
        # Información FUID
        st.info("""
        - Analizará el contenido con comprensión contextual
        - Clasificará automáticamente por área/serie/subsérie
        - Organizará en carpetas estructuradas
        - Generará metadatos completos de clasificación
        """)
        
        # Formulario URL
        url = st.text_input(
            "📎 URL del documento o carpeta",
            placeholder="https://drive.google.com/drive/folders/... o https://drive.google.com/file/d/...",
            key="url_input"
        )
        
        version = st.text_input("🔢 Versión", "1.0", key="version_url")
        
        # Botón de procesamiento
        button_text = "📁 Procesar con Clasificación FUID"
        
        if st.button(button_text, use_container_width=True, disabled=not url, key="btn_process_url"):
            process_url_service(url, version, "fuid")

    # --- BOTÓN DE VOLVER ---
    st.markdown("---")
    if st.button("⬅ Volver al Dashboard", use_container_width=True):
        cambiar_vista("dashboard")

    st.markdown('</div>', unsafe_allow_html=True)


def process_url_service(url, version, service_type):
    """Función para procesar servicios por URL - VERSIÓN CORREGIDA"""
    try:
        # Mostrar progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Iniciar procesamiento
        progress_text = "Clasificando con IA contextual..."
        status_text.text("Iniciando procesamiento...")
        progress_bar.progress(10)
        
        status_text.text(progress_text)
        progress_bar.progress(30)
        
        # Determinar endpoint y cuerpo
        endpoint = f"{API_BASE}/fuid/procesar-url"
        
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        request_body = {"url": url, "version": version}
        
        # TIMEOUT AUMENTADO A 10 MINUTOS
        resp = requests.post(endpoint, json=request_body, headers=headers, timeout=600)
        
        status_text.text("Finalizando...")
        progress_bar.progress(90)
        
        if resp.ok:
            data = resp.json()
            progress_bar.progress(100)
            status_text.text("Completado")
            
            # Mostrar resultado FUID
            display_fuid_result(data)
                
        else:
            error_data = resp.json()
            st.markdown(f"""
            <div class="result-error">
                <h5>⚠️ Error en el Procesamiento</h5>
                <strong>Status Code:</strong> {resp.status_code}<br>
                <strong>Detalle:</strong> {error_data.get('detail', error_data.get('error', 'Error desconocido'))}<br>
                <strong>Sugerencia:</strong> Verifica que la URL sea accesible públicamente y vuelve a intentar.
            </div>
            """, unsafe_allow_html=True)
            
    except requests.exceptions.Timeout:
        st.markdown(f"""
        <div class="result-error">
            <h5>⏰ Timeout del Servidor</h5>
            <strong>Detalle:</strong> El servidor tardó demasiado en responder<br>
            <strong>Sugerencia:</strong> Intenta con menos documentos o más tarde.
        </div>
        """, unsafe_allow_html=True)
    except requests.exceptions.ConnectionError:
        st.markdown(f"""
        <div class="result-error">
            <h5>🔌 Error de Conexión</h5>
            <strong>Detalle:</strong> No se pudo conectar con el servidor<br>
            <strong>Sugerencia:</strong> Verifica que el servidor esté ejecutándose en {API_BASE}
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
        <div class="result-error">
            <h5>⚠️ Error Inesperado</h5>
            <strong>Detalle:</strong> {str(e)}<br>
            <strong>Sugerencia:</strong> Verifica tu conexión a internet y vuelve a intentar.
        </div>
        """, unsafe_allow_html=True)
    finally:
        # Limpiar después de 2 segundos
        time.sleep(2)
        progress_bar.empty()
        status_text.empty()


def display_fuid_result(data):
    """Mostrar resultado del procesamiento FUID - VERSIÓN CON COLORES CORREGIDOS"""
    
    # CSS adicional para corregir colores
    st.markdown("""
    <style>
        .expediente-card {
            border: 1px solid #81c784; 
            padding: 15px; 
            margin-bottom: 15px; 
            border-radius: 8px; 
            background-color: #1e1e1e !important;
            color: white !important;
        }
        .expediente-card strong {
            color: #81c784 !important;
        }
        .resultado-card {
            border: 1px solid #bbdefb; 
            padding: 12px; 
            margin-bottom: 10px; 
            border-radius: 6px; 
            background-color: #2d2d2d !important;
            color: white !important;
        }
        .resultado-card strong {
            color: #bbdefb !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar información básica primero
    st.markdown(f"""
    <div class="result-success">
        <h5>✅ Procesamiento FUID Completado</h5>
        <strong>Estado:</strong> {data.get('estado', 'N/A')}<br>
        <strong>Mensaje:</strong> {data.get('mensaje', 'N/A')}<br>
        <strong>Documentos procesados:</strong> {data.get('procesados', 0)}<br>
    </div>
    """, unsafe_allow_html=True)
    
    # MOSTRAR EXPEDIENTES
    expedientes_creados = data.get('expedientes_creados', [])
    
    if expedientes_creados and len(expedientes_creados) > 0:
        st.markdown("---")
        st.subheader("📂 Expedientes Creados:")
        
        for expediente in expedientes_creados:
            # Asegurarse de que todos los valores son strings
            fuid = str(expediente.get('fuid', 'N/A'))
            codigo = str(expediente.get('codigo', 'N/A'))
            documentos = str(expediente.get('documentos', 'N/A'))
            unidad_documental = str(expediente.get('unidad_documental', 'N/A'))
            
            st.markdown(f"""
            <div class="expediente-card">
                <strong>🆔 FUID:</strong> {fuid}<br>
                <strong>📋 Código:</strong> {codigo}<br>
                <strong>📄 Documentos:</strong> {documentos}<br>
                <strong>🏢 Unidad Documental:</strong> {unidad_documental}
            </div>
            """, unsafe_allow_html=True)
    
    # Mostrar resultados detallados si existen
    resultados = data.get('resultados', [])
    if resultados and len(resultados) > 0:
        st.markdown("---")
        st.subheader("📊 Resultados Detallados:")
        
        for i, resultado in enumerate(resultados):
            documento = str(resultado.get('documento', 'N/A'))
            clasificacion = str(resultado.get('clasificacion', 'N/A'))
            unidad_documental = str(resultado.get('unidad_documental', 'N/A'))
            confianza = str(resultado.get('confianza', 'N/A'))
            ruta_final = str(resultado.get('ruta_final', 'N/A'))
            
            st.markdown(f"""
            <div class="resultado-card">
                <strong>📄 Documento {i+1}:</strong> {documento}<br>
                <strong>🏷️ Clasificación:</strong> {clasificacion}<br>
                <strong>🏢 Unidad:</strong> {unidad_documental}<br>
                <strong>🎯 Confianza:</strong> {confianza}<br>
                <strong>📁 Ruta:</strong> <small>{ruta_final}</small>
            </div>
            """, unsafe_allow_html=True)
