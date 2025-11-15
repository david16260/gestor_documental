# dashboard.py - Pantalla principal del sistema (Dashboard)
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"


def dashboard_page(cambiar_vista):
    """Pantalla principal del sistema (Dashboard)."""

    # --- Verifica sesión ---
    if "token" not in st.session_state or not st.session_state.token:
        st.warning("🔒 No has iniciado sesión.")
        st.stop()

    usuario = st.session_state.get("usuario_nombre", "Desconocido")

    # --- ESTILOS VISUALES MEJORADOS ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #f1f8e9 0%, #f9fbe7 50%, #ffffff 100%);
            font-family: 'Inter', sans-serif;
        }

        /* HEADER UNIFICADO - 3cm debajo de pestañas */
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

        .main-container {
            margin-top: 180px;
            text-align: center;
            animation: fadeInUp 0.8s ease;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h2 {
            color: #66bb6a;
            font-weight: 700;
            font-size: 42px;
            margin-bottom: 15px;
            letter-spacing: -0.5px;
        }

        p {
            color: #81c784;
            font-size: 18px;
            margin-bottom: 50px;
            font-weight: 500;
        }

        /* BOTONES PRINCIPALES - MÁS LARGOS Y ELEGANTES */
        div[data-testid="stButton"] > button {
            display: block;
            width: 650px !important;
            height: 85px !important;
            border-radius: 16px !important;
            font-size: 32px !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            border: none !important;
            margin: 25px auto !important;
            cursor: pointer !important;
            box-shadow: 0 4px 20px rgba(129, 199, 132, 0.3) !important;
            transition: all 0.35s ease !important;
            position: relative;
            overflow: hidden;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
            letter-spacing: 0.5px !important;
        }
        
        /* Forzar color blanco opaco en el texto */
        div[data-testid="stButton"] > button p,
        div[data-testid="stButton"] > button span,
        div[data-testid="stButton"] > button div {
            color: #ffffff !important;
            opacity: 1 !important;
        }

        div[data-testid="stButton"] > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        div[data-testid="stButton"] > button:hover::before {
            width: 600px;
            height: 600px;
        }

        div[data-testid="stButton"] > button:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(129, 199, 132, 0.4);
        }

        div[data-testid="stButton"] > button:active {
            transform: translateY(-2px);
        }

        /* Colores verdes profesionales para cada botón */
        div[data-testid="stButton"]:nth-of-type(1) > button {
            background: linear-gradient(135deg, #81c784 0%, #66bb6a 100%);
        }
        div[data-testid="stButton"]:nth-of-type(2) > button {
            background: linear-gradient(135deg, #aed581 0%, #9ccc65 100%);
        }
        div[data-testid="stButton"]:nth-of-type(3) > button {
            background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
        }
        div[data-testid="stButton"]:nth-of-type(4) > button {
            background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        }
        div[data-testid="stButton"]:nth-of-type(5) > button {
            background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
        }
        div[data-testid="stButton"]:nth-of-type(6) > button {
            background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        }

        /* Footer profesional */
        .footer {
            margin-top: 70px;
            text-align: center;
            font-size: 14px;
            color: #81c784;
            font-weight: 500;
            padding: 18px;
            background: rgba(174, 213, 129, 0.1);
            border-radius: 12px;
            margin-left: 20%;
            margin-right: 20%;
            border: 1px solid rgba(174, 213, 129, 0.2);
        }

        /* Animación de entrada para los botones */
        div[data-testid="stButton"] {
            animation: slideIn 0.5s ease forwards;
            opacity: 0;
        }

        div[data-testid="stButton"]:nth-of-type(1) {
            animation-delay: 0.1s;
        }
        div[data-testid="stButton"]:nth-of-type(2) {
            animation-delay: 0.2s;
        }
        div[data-testid="stButton"]:nth-of-type(3) {
            animation-delay: 0.3s;
        }
        div[data-testid="stButton"]:nth-of-type(4) {
            animation-delay: 0.4s;
        }
        div[data-testid="stButton"]:nth-of-type(5) {
            animation-delay: 0.5s;
        }
        div[data-testid="stButton"]:nth-of-type(6) {
            animation-delay: 0.6s;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        /* Ocultar botones de header de streamlit - COMPLETAMENTE INVISIBLES */
        div[data-testid="column"]:has(button[key="dash_hidden"]),
        div[data-testid="column"]:has(button[key="logout_hidden"]) {
            position: absolute !important;
            top: -9999px !important;
            left: -9999px !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
            overflow: hidden !important;
            z-index: -9999 !important;
            display: none !important;
        }
        
        button[key="dash_hidden"],
        button[key="logout_hidden"] {
            width: 0 !important;
            height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            position: absolute !important;
            top: -9999px !important;
            left: -9999px !important;
            font-size: 0 !important;
            line-height: 0 !important;
            display: none !important;
        }
        
        /* Ocultar las columnas que contienen estos botones */
        .stColumns > div:has(button[key="dash_hidden"]),
        .stColumns > div:has(button[key="logout_hidden"]) {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- HEADER UNIFICADO MEJORADO ---
    # Primero creamos los botones funcionales ocultos
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        dash_btn = st.button("🏠 Dashboard", key="dash_hidden")
    with col3:
        logout_btn = st.button("🚪 Cerrar sesión", key="logout_hidden")
    
    # Luego el HTML visual
    st.markdown(f"""
        <div class="unified-header">
            <form action="" method="get">
                <button type="submit" name="dash" class="header-btn" style="border:none; cursor:pointer;">
                    🏠 Volver
                </button>
            </form>
            <div class="user-info">
                👤 {usuario} | Sesión activa
            </div>
            <form action="" method="get">
                <button type="submit" name="logout" class="header-btn" style="border:none; cursor:pointer;">
                    🚪 Cerrar sesión
                </button>
            </form>
        </div>
        <script>
            // Conectar botones HTML con botones Streamlit ocultos
            document.addEventListener('DOMContentLoaded', function() {{
                const dashBtn = document.querySelector('button[name="dash"]');
                const logoutBtn = document.querySelector('button[name="logout"]');
                
                if (dashBtn) {{
                    dashBtn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const realBtn = document.querySelector('button[key="dash_hidden"]');
                        if (realBtn) realBtn.click();
                    }});
                }}
                
                if (logoutBtn) {{
                    logoutBtn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const realBtn = document.querySelector('button[key="logout_hidden"]');
                        if (realBtn) realBtn.click();
                    }});
                }}
            }});
        </script>
    """, unsafe_allow_html=True)
    
    # Procesar acciones
    if dash_btn:
        cambiar_vista("dashboard")
    if logout_btn:
        st.session_state.token = None
        st.session_state.usuario_nombre = None
        cambiar_vista("login")

    # --- CONTENIDO PRINCIPAL ---
    st.markdown("""
        <div class="main-container">
            <h2>📂 Gestor Documental</h2>
            <p>Selecciona una opción para continuar</p>
        </div>
    """, unsafe_allow_html=True)

    # --- BOTONES FUNCIONALES PRINCIPALES ---
    st.write("")
    
    # Botón 1: Subir Documento
    if st.button("📁 Subir Documento"):
        cambiar_vista("documentos")

    # Botón 2: Procesar Documentos
    if st.button("🔧 Procesar Documentos"):
        cambiar_vista("procesar_documentos")

    # Botón 3: Ver Versiones Vigentes
    if st.button("📄 Ver Versiones Vigentes"):
        cambiar_vista("versiones")

    # Botón 4: Ver Historial de Documentos
    if st.button("📜 Ver Historial de Documentos"):
        cambiar_vista("historial")

    # BOTÓN NUEVO 5: Exportación SGDEA
    if st.button("📤 Exportación SGDEA"):
        cambiar_vista("exportacion")
        
    # NUEVO BOTÓN PARA GENERACIÓN XML
    if st.button("📝 Generar XML TRD"):
        cambiar_vista("xml_generation")
        
    # NUEVO BOTÓN PARA ÍNDICES FOLIADOS
    if st.button("📑 Generar Índices Foliados"):
        cambiar_vista("indices_foliados")

    # --- FOOTER ---
    st.markdown("""
        <div class="footer">
            © 2025 Gestor Documental | Sistema de Gestión de Documentos
        </div>
    """, unsafe_allow_html=True)