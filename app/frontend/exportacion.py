# exportacion.py - Página de exportación SGDEA
import streamlit as st
import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import io

API_BASE = "http://127.0.0.1:8000"

def exportacion_page(cambiar_vista):
    """Pantalla de exportación de datos SGDEA."""
    
    # --- Verifica sesión ---
    if "token" not in st.session_state or not st.session_state.token:
        st.warning("🔒 No has iniciado sesión.")
        st.stop()

    usuario = st.session_state.get("usuario_nombre", "Desconocido")
    
    # --- ESTILOS ESPECÍFICOS PARA EXPORTACIÓN CON PALETA VERDE ---
    st.markdown("""
    <style>
        .export-header {
            background: linear-gradient(135deg, #81c784 0%, #66bb6a 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 4px 20px rgba(129, 199, 132, 0.3);
        }
        
        .export-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .export-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .status-message {
            background: linear-gradient(135deg, #aed581 0%, #9ccc65 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: 600;
        }
        
        .format-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin: 5px;
        }
        
        .json-badge {
            background: #c8e6c9;
            color: #2e7d32;
            border: 1px solid #81c784;
        }
        
        .xml-badge {
            background: #a5d6a7;
            color: #1b5e20;
            border: 1px solid #66bb6a;
        }
        
        .download-btn {
    background: linear-gradient(135deg, #2596be 0%, #1e87b0 100%);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
    margin-top: 15px;
}
        
        .download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(37, 150, 190, 0.4);
}
        
        .upload-section {
            background: #f1f8e9;
            border: 2px dashed #c8e6c9;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
        }
        
        .steps-container {
            background: linear-gradient(135deg, #81c784 0%, #4caf50 100%);
            border-radius: 12px;
            padding: 25px;
            color: white;
            margin-top: 30px;
        }
        
        .step-item {
            display: flex;
            align-items: center;
            margin: 15px 0;
            font-size: 16px;
        }
        
        .step-number {
            background: white;
            color: #4caf50;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
            flex-shrink: 0;
        }
        
        /* HEADER UNIFICADO - Mismo estilo que dashboard */
        .unified-header {
            position: fixed;
            top: 85px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 1100px;
            background: linear-gradient(135deg, #81c784 0%, #aed581 100%);
            border-radius: 12px;
            padding: 12px 20px;
            box-shadow: 0 4px 20px rgba(129, 199, 132, 0.25);
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
        }

        .header-btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            backdrop-filter: blur(10px);
        }
        .stApp {
    background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    color: #000000 !important;
}
p, h1, h2, h3, h4, h5, h6, div, span {
    color: #000000 !important;
}

.main .block-container {
    background: #ffffff;
}

        .header-btn:hover {
            background: rgba(255,255,255,0.35);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(255,255,255,0.3);
        }

        .user-info {
            flex: 1;
            text-align: center;
            color: white;
            font-size: 14px;
            font-weight: 600;
            background: rgba(255,255,255,0.15);
            padding: 10px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
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
div[data-testid="stFileUploader"] {
    background: #69bc6c !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

div[data-testid="stFileUploader"] * {
    color: white !important;
}

div[data-testid="stFileUploader"] button {
    background: rgba(255,255,255,0.2) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #81db85 0%, #69bc6c 100%) !important;
    color: white !important;
    border: none !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg, #81db85 0%, #69bc6c 100%) !important;
    color: white !important;
    border: none !important;
}
div[data-testid="stJson"] {
    background: #69bc6c !important;
    border-radius: 8px !important;
    padding: 15px !important;
}

div[data-testid="stJson"] * {
    color: white !important;
}

div[data-testid="stCode"] {
    background: #69bc6c !important;
    border-radius: 8px !important;
}

div[data-testid="stCode"] * {
    color: white !important;
}
    </style>
    """, unsafe_allow_html=True)
    
    # --- HEADER DE EXPORTACIÓN ---
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        dash_btn = st.button("🏠 Dashboard", key="export_dash_hidden")
    with col3:
        logout_btn = st.button("🚪 Cerrar sesión", key="export_logout_hidden")
    
    # Header visual
    st.markdown(f"""
        <div class="unified-header">
            <form action="" method="get">
                <button type="submit" name="dash" class="header-btn" style="border:none; cursor:pointer;">
                    🏠 Volver
                </button>
            </form>
            <div class="user-info">
                👤 {usuario} | Panel de Exportación SGDEA
            </div>
            <form action="" method="get">
                <button type="submit" name="logout" class="header-btn" style="border:none; cursor:pointer;">
                    🚪 Cerrar sesión
                </button>
            </form>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const dashBtn = document.querySelector('button[name="dash"]');
                const logoutBtn = document.querySelector('button[name="logout"]');
                
                if (dashBtn) {{
                    dashBtn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const realBtn = document.querySelector('button[key="export_dash_hidden"]');
                        if (realBtn) realBtn.click();
                    }});
                }}
                
                if (logoutBtn) {{
                    logoutBtn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const realBtn = document.querySelector('button[key="export_logout_hidden"]');
                        if (realBtn) realBtn.click();
                    }});
                }}
            }});
        </script>
    """, unsafe_allow_html=True)
    
    # Procesar acciones del header
    if dash_btn:
        cambiar_vista("dashboard")
    if logout_btn:
        st.session_state.token = None
        st.session_state.usuario_nombre = None
        cambiar_vista("login")
    
    # --- CONTENIDO PRINCIPAL ---
    st.markdown("""
        <div style="margin-top: 120px;">
            <div class="export-header">
                <h1 style="margin:0; color:white;">📤 Exportación de Datos SGDEA</h1>
                <p style="margin:5px 0 0 0; color:white; opacity:0.9;">
                    Sistema de Gestión de Datos Empresariales Avanzado
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Mensaje de estado
    st.markdown("""
        <div class="status-message">
            ✅ <strong>Exportando datos en formato XML. Listo para compartir con otros sistemas SGDEA.</strong>
        </div>
    """, unsafe_allow_html=True)
    
    # Sección de datos del sistema
    st.subheader("📊 Datos del Sistema")
    st.write("Información de tu sistema en formatos universales para compartir")
    
    # Tarjetas de exportación
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="export-card">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span class="format-badge json-badge">{ }</span>
                    <h3 style="margin: 0 0 0 10px;">JSON</h3>
                </div>
                <p style="color: #666; margin-bottom: 20px;">
                    Formato ideal para aplicaciones web modernas y APIs REST. 
                    Estructura ligera y fácil de procesar en JavaScript.
                </p>
        """, unsafe_allow_html=True)
        
        if st.button("📥 Descargar JSON", key="json_export", use_container_width=True):
            generar_descarga('json')
    
    with col2:
        st.markdown("""
            <div class="export-card">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span class="format-badge xml-badge">&lt;/&gt;</span>
                    <h3 style="margin: 0 0 0 10px;">XML</h3>
                </div>
                <p style="color: #666; margin-bottom: 20px;">
                    Estándar ampliamente utilizado en sistemas empresariales. 
                    Compatible con legacy systems y aplicaciones corporativas.
                </p>
        """, unsafe_allow_html=True)
        
        if st.button("📥 Descargar XML", key="xml_export", use_container_width=True):
            generar_descarga('xml')
    
    # Sección de importación de datos externos
    st.markdown("---")
    st.subheader("📥 Datos Externos")
    st.write("Importar información desde otros sistemas SGDEA compatibles")
    
    st.markdown("""
        <div class="upload-section">
            <h4 style="color: #666; margin-bottom: 20px;">🔄 Cargar Archivo SGDEA</h4>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Selecciona un archivo local generado por sistemas SGDEA compatibles",
        type=['xml', 'json'],
        key="sgdea_upload"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Archivo cargado: **{uploaded_file.name}**")
        
        # Mostrar vista previa
        if st.button("🔍 Vista Previa", key="preview_btn"):
            mostrar_vista_previa(uploaded_file)
        
        if st.button("⚙️ Procesar Archivo", key="process_btn"):
            procesar_archivo(uploaded_file)
    
    # Pasos siguientes después de la descarga
    st.markdown("---")
    st.markdown("""
        <div class="steps-container">
            <h3 style="color: white; margin-bottom: 20px;">🚀 ¿Qué sigue después de descargar?</h3>
    """, unsafe_allow_html=True)
    
    pasos = [
        "Comparte el archivo con otros sistemas SGDEA compatibles",
        "Importa los datos en tu aplicación o sistema de destino", 
        "Valida la integridad de los datos en el sistema receptor",
        "Configura la sincronización automática si es necesario"
    ]
    
    for i, paso in enumerate(pasos, 1):
        st.markdown(f"""
            <div class="step-item">
                <div class="step-number">{i}</div>
                <div>{paso}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; color: #666; font-size: 14px;">
            <hr style="margin: 30px 0;">
            <strong>Sistema SGDEA - Panel de Exportación de Datos</strong><br>
            127.0.0.1:8000 | Panel - C | ID: 5212155
        </div>
    """, unsafe_allow_html=True)

def generar_descarga(formato):
    """Genera y descarga el archivo en el formato especificado"""
    
    try:
        # Datos de ejemplo del sistema (en un caso real, vendrían de la API)
        datos_sistema = {
            "sistema": "SGDEA",
            "version": "2.1.5", 
            "panel": "C",
            "usuario": st.session_state.get("usuario_nombre", "Desconocido"),
            "id_usuario": st.session_state.get("usuario_id", "N/A"),
            "timestamp": datetime.now().isoformat(),
            "estadisticas": {
                "documentos_totales": 245,
                "usuarios_activos": 150,
                "almacenamiento_mb": 1250,
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            },
            "configuracion": {
                "exportacion_automatica": True,
                "formato_predeterminado": "xml",
                "compresion_habilitada": False
            }
        }
        
        if formato == 'json':
            json_data = json.dumps(datos_sistema, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="⬇️ Descargar JSON ahora",
                data=json_data,
                file_name=f"sgdea_export_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                key="download_json_final"
            )
            
        elif formato == 'xml':
            # Convertir datos a XML
            root = ET.Element("sgdea")
            
            # Elementos básicos
            for key, value in datos_sistema.items():
                if key == "estadisticas":
                    stats_elem = ET.SubElement(root, "estadisticas")
                    for stat_key, stat_value in datos_sistema["estadisticas"].items():
                        stat = ET.SubElement(stats_elem, stat_key)
                        stat.text = str(stat_value)
                elif key == "configuracion":
                    config_elem = ET.SubElement(root, "configuracion")
                    for config_key, config_value in datos_sistema["configuracion"].items():
                        config = ET.SubElement(config_elem, config_key)
                        config.text = str(config_value)
                else:
                    elem = ET.SubElement(root, key)
                    elem.text = str(value)
            
            xml_string = ET.tostring(root, encoding='unicode', method='xml')
            
            st.download_button(
                label="⬇️ Descargar XML ahora",
                data=xml_string,
                file_name=f"sgdea_export_{datetime.now().strftime('%Y%m%d_%H%M')}.xml",
                mime="application/xml",
                key="download_xml_final"
            )
            
        st.success(f"✅ Archivo {formato.upper()} generado correctamente")
        
    except Exception as e:
        st.error(f"❌ Error generando archivo: {str(e)}")

def mostrar_vista_previa(archivo):
    """Muestra una vista previa del archivo cargado"""
    
    try:
        contenido = archivo.getvalue().decode('utf-8')
        
        st.subheader("👁️ Vista Previa del Archivo")
        
        if archivo.name.endswith('.json'):
            try:
                datos = json.loads(contenido)
                st.json(datos)
            except json.JSONDecodeError:
                st.error("El archivo no es un JSON válido")
                st.code(contenido)
        
        elif archivo.name.endswith('.xml'):
            st.code(contenido, language='xml')
            
    except Exception as e:
        st.error(f"Error al leer el archivo: {str(e)}")

def procesar_archivo(archivo):
    """Procesa el archivo cargado"""
    
    try:
        with st.spinner("🔄 Procesando archivo..."):
            # Simular procesamiento
            import time
            time.sleep(2)
            
            st.success("✅ Archivo procesado correctamente")
            
            # Mostrar resumen
            st.info(f"""
            **Resumen del procesamiento:**
            - Archivo: {archivo.name}
            - Tamaño: {len(archivo.getvalue())} bytes
            - Tipo: {archivo.type if hasattr(archivo, 'type') else 'N/A'}
            - Procesado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """)
            
    except Exception as e:
        st.error(f"❌ Error procesando archivo: {str(e)}")