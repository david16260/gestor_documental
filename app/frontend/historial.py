import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"


def historial_page(cambiar_vista):
    """Pantalla del historial de documentos con estilo visual de tarjetas."""

    # --- Validar sesión ---
    if "token" not in st.session_state or not st.session_state.token:
        st.warning("🔒 No has iniciado sesión.")
        st.stop()

    usuario = st.session_state.get("usuario_nombre", "Desconocido")

    # --- Estilos visuales ---
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #e8f5e9, #c8e6c9);
            font-family: 'Segoe UI', Tahoma, sans-serif;
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
            max-width: 750px;
            border: 1px solid #c8e6c9;
            margin-left: auto;
            margin-right: auto;
        }

        .version-card {
            background: #f9fbe7;
            border-left: 6px solid #4caf50;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .version-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 14px rgba(0,0,0,0.1);
        }

        .version-title {
            font-weight: 700;
            color: #2e7d32;
            font-size: 17px;
            margin-bottom: 4px;
        }

        .version-info {
            color: #33691e;
            font-size: 14px;
            margin-left: 10px;
        }

        button[data-baseweb="button"] {
            display: block;
            width: 100% !important;
            height: 60px !important;
            border-radius: 14px !important;
            font-size: 20px !important;
            font-weight: bold !important;
            color: white !important;
            border: none !important;
            margin-top: 15px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        }

        div[data-testid="stButton"]:nth-of-type(1) button {
            background: linear-gradient(135deg, #4caf50, #388e3c);
        }
        div[data-testid="stButton"]:nth-of-type(2) button {
            background: linear-gradient(135deg, #f44336, #e53935);
        }

    </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    st.markdown(f"""
    <div class="header">
        <div>👤 {usuario} | Historial de documentos</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

    # --- CONTENIDO ---
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.title("📜 Historial de documentos")
    st.markdown("Consulta las versiones anteriores de un documento específico por su nombre.")

    nombre_archivo = st.text_input("📄 Nombre del archivo (ejemplo: Manual_Seguridad.pdf)")

    if st.button("🔎 Buscar historial"):
        if not nombre_archivo:
            st.warning("⚠️ Debes ingresar el nombre del archivo.")
        else:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            try:
                resp = requests.get(f"{API_BASE}/documentos/historial?nombre_archivo={nombre_archivo}", headers=headers)

                if resp.ok:
                    data = resp.json()
                    historial = data.get("historial", [])

                    if historial:
                        st.success(f"📄 Se encontraron **{len(historial)} versiones** para **{nombre_archivo}**.")

                        st.markdown("<h4 style='color:#1b5e20; margin-top:20px;'>📋 Historial de versiones:</h4>", unsafe_allow_html=True)

                        for i, v in enumerate(historial, start=1):
                            version_html = f"""
                            <div class="version-card">
                                <div class="version-title">🔢 Versión {v.get("version", "-")}</div>
                                <div class="version-info">📅 <b>Fecha:</b> {v.get("fecha_subida", "-")}</div>
                                <div class="version-info">👤 <b>Usuario:</b> {v.get("usuario", "-")}</div>
                            </div>
                            """
                            st.markdown(version_html, unsafe_allow_html=True)

                    else:
                        st.warning(f"⚠️ No se encontró historial para **{nombre_archivo}**.")
                else:
                    st.error(resp.json().get("detail", "❌ Error al obtener el historial."))
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")

    if st.button("⬅ Volver al panel principal"):
        cambiar_vista("dashboard")

    st.markdown('</div>', unsafe_allow_html=True)
