# indices_foliados.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

def indices_foliados_page(cambiar_vista):
    """Pantalla para generar índices foliados."""
    
    # --- Verifica sesión ---
    if "token" not in st.session_state or not st.session_state.token:
        st.warning("🔒 No has iniciado sesión.")
        st.stop()

    usuario = st.session_state.get("usuario_nombre", "Desconocido")
    
    # --- ESTILOS CON PALETA VERDE ---
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
            background: linear-gradient(135deg, #2596be 0%, #1e87b0 100%) !important;
            color: white !important;
            border: none !important;
        }

        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, #1e87b0 0%, #18779f 100%) !important;
            color: white !important;
            border: none !important;
        }
        
        .header-indices {
            background: linear-gradient(135deg, #81c784 0%, #66bb6a 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 4px 20px rgba(129, 199, 132, 0.3);
        }
        
        .indice-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        
        .stats-container {
            background: linear-gradient(135deg, #aed581 0%, #9ccc65 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }
        
        /* HEADER UNIFICADO */
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
    </style>
    """, unsafe_allow_html=True)
    
    # --- HEADER ---
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        dash_btn = st.button("🏠 Dashboard", key="indices_dash_hidden")
    with col3:
        logout_btn = st.button("🚪 Cerrar sesión", key="indices_logout_hidden")
    
    # Header visual
    st.markdown(f"""
        <div class="unified-header">
            <form action="" method="get">
                <button type="submit" name="dash" class="header-btn" style="border:none; cursor:pointer;">
                    🏠 Volver
                </button>
            </form>
            <div class="user-info">
                👤 {usuario} | Índices Foliados
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
                        const realBtn = document.querySelector('button[key="indices_dash_hidden"]');
                        if (realBtn) realBtn.click();
                    }});
                }}
                
                if (logoutBtn) {{
                    logoutBtn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const realBtn = document.querySelector('button[key="indices_logout_hidden"]');
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
            <div class="header-indices">
                <h1 style="margin:0; color:white;">📑 Generador de Índices Foliados</h1>
                <p style="margin:5px 0 0 0; color:white; opacity:0.9;">
                    Sistema automatizado de numeración y organización documental
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- BOTÓN PARA GENERAR ÍNDICE ---
    st.markdown("""
        <div class="indice-card">
            <h3>🔢 Generar Índice Foliado</h3>
            <p>Obtén un listado organizado de todos tus documentos con numeración foliada automática.</p>
    """, unsafe_allow_html=True)
    
    if st.button("📋 Generar Índice Foliado", use_container_width=True, key="btn_generar_indice"):
        generar_indice_foliado()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- INFORMACIÓN ADICIONAL ---
    st.markdown("""
        <div class="indice-card">
            <h3>📊 ¿Qué es un índice foliado?</h3>
            <p>Un índice foliado es un sistema de numeración consecutiva que asigna un número único a cada página 
            o documento, facilitando la localización y referencia de la información.</p>
            
            <div style="background: #f1f8e9; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <strong>Características del sistema:</strong>
                <ul style="margin: 10px 0;">
                    <li>Numeración automática y consecutiva</li>
                    <li>Organización por orden de procesamiento</li>
                    <li>Información de páginas de inicio y fin</li>
                    <li>Exportación en formato CSV</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

def generar_indice_foliado():
    """Función para generar y mostrar el índice foliado"""
    
    try:
        with st.spinner("🔄 Generando índice foliado..."):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            resp = requests.get(f"{API_BASE}/documentos/indice_foliado", headers=headers)
            
            if resp.ok:
                data = resp.json()
                
                # Mostrar estadísticas
                st.markdown(f"""
                    <div class="stats-container">
                        <h4 style="color: white; margin:0;">📈 Estadísticas del Índice</h4>
                        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold;">{data.get('total_documentos', 0)}</div>
                                <div style="font-size: 14px;">Documentos</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold;">{data.get('total_paginas', 0)}</div>
                                <div style="font-size: 14px;">Páginas estimadas</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold;">{data.get('usuario_id', 'N/A')}</div>
                                <div style="font-size: 14px;">ID Usuario</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Mostrar tabla de índice
                if data.get('indice'):
                    df = pd.DataFrame(data['indice'])
                    
                    # Renombrar columnas para mejor visualización
                    df = df.rename(columns={
                        'orden': 'Orden',
                        'nombre_archivo': 'Documento',
                        'tamano_kb': 'Tamaño (KB)',
                        'pagina_inicio': 'Página Inicio',
                        'pagina_fin': 'Página Fin',
                        'fecha': 'Fecha'
                    })
                    
                    st.subheader("📋 Índice Foliado Detallado")
                    st.dataframe(df, use_container_width=True)
                    
                    # Botón para descargar CSV
                    st.markdown("---")
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if st.button("📥 Descargar CSV", use_container_width=True, key="btn_descargar_csv"):
                            descargar_csv_indice()
                    
                    with col2:
                        if st.button("🔄 Generar Nuevo Índice", use_container_width=True, key="btn_regenerar"):
                            st.rerun()
                
                else:
                    st.warning("No se encontraron documentos para generar el índice foliado.")
                    
            else:
                error_data = resp.json()
                st.error(f"❌ Error al generar índice: {error_data.get('detail', 'Error desconocido')}")
                
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")

def descargar_csv_indice():
    """Función para descargar el índice en formato CSV"""
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        resp = requests.get(f"{API_BASE}/documentos/indice_foliado?formato=csv", headers=headers)
        
        if resp.ok:
            # Crear archivo CSV para descarga
            csv_content = resp.content
            usuario = st.session_state.get("usuario_nombre", "user")
            fecha = datetime.now().strftime("%Y%m%d_%H%M")
            
            st.download_button(
                label="⬇️ Descargar CSV ahora",
                data=csv_content,
                file_name=f"indice_foliado_{usuario}_{fecha}.csv",
                mime="text/csv",
                key="download_csv_final"
            )
            
        else:
            st.error("Error al generar el archivo CSV")
            
    except Exception as e:
        st.error(f"Error al descargar CSV: {str(e)}")