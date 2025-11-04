import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

def versiones_page(cambiar_vista):
    st.set_page_config(page_title="📗 Versiones Vigentes", layout="centered")

    # --- Asegurar sesión ---
    if "token" not in st.session_state:
        st.session_state.token = None
    if "usuario_nombre" not in st.session_state:
        st.session_state.usuario_nombre = None

    # --- ESTILOS ---
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #e8f5e9, #c8e6c9);
            font-family: 'Segoe UI', Tahoma, sans-serif !important;
        }

        .container {
            background: #ffffff;
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin-top: 120px;
            max-width: 700px;
            border: 1px solid #c8e6c9;
            margin-left: auto;
            margin-right: auto;
        }

        /* --- Botones dinámicos --- */
        .stButton > button {
            display: block;
            width: 100% !important;
            height: 65px !important;
            border-radius: 14px !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            color: white !important;
            border: none !important;
            margin-top: 18px !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
            transition: all 0.25s ease-in-out !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Verde principal */
        div[data-testid="stButton"]:nth-of-type(1) button {
            background: linear-gradient(135deg, #43a047, #2e7d32);
        }
        div[data-testid="stButton"]:nth-of-type(1) button:hover {
            background: linear-gradient(135deg, #66bb6a, #43a047);
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 20px rgba(76, 175, 80, 0.35);
        }

        /* Rojo final */
        div[data-testid="stButton"]:nth-of-type(2) button {
            background: linear-gradient(135deg, #e53935, #b71c1c);
        }
        div[data-testid="stButton"]:nth-of-type(2) button:hover {
            background: linear-gradient(135deg, #ef5350, #e53935);
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 20px rgba(239, 83, 80, 0.35);
        }

        h1, h2, h3 {
            color: #2e7d32 !important;
            font-weight: 700 !important;
            text-align: center !important;
        }

        .footer {
            margin-top: 60px;
            text-align: center;
            font-size: 14px;
            color: #558b2f;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGIN ---
    if not st.session_state.token:
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.subheader("🔐 Iniciar sesión")

        with st.form("login-form"):
            email = st.text_input("📧 Correo electrónico", placeholder="usuario@correo.com")
            password = st.text_input("🔑 Contraseña", type="password")
            login_btn = st.form_submit_button("➡️ Iniciar sesión")

        if login_btn:
            try:
                res = requests.post(f"{API_BASE}/auth/login", data={"username": email, "password": password})
                if res.ok:
                    data = res.json()
                    st.session_state.token = data.get("access_token")
                    st.session_state.usuario_nombre = data.get("nombre", "Usuario")
                    st.success("✅ Sesión iniciada correctamente")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
            except Exception as e:
                st.error(f"⚠️ Error de conexión: {e}")

        st.markdown('</div>', unsafe_allow_html=True)
        return

    # --- CONTENIDO PRINCIPAL ---
    with st.container():
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown("## 📘 Versiones Vigentes")
        st.info("Aquí podrás ver las versiones activas y sus detalles más recientes.")

        if st.button("📂 Consultar versiones"):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                res = requests.get(f"{API_BASE}/documentos/versiones", headers=headers)
                if res.ok:
                    data = res.json()
                    documentos = data.get("documentos", [])

                    if documentos:
                        st.success(f"📄 Se encontraron {len(documentos)} documento(s) con versiones registradas.")
                        for doc in documentos:
                            with st.expander(f"📘 {doc['nombre']} ({len(doc.get('versiones', []))} versiones)"):
                                for v in doc["versiones"]:
                                    st.markdown(
                                        f"- 🔖 **Versión:** {v['version']} | 📅 {v['fecha_subida']} | 👤 {v['usuario']}"
                                    )
                    else:
                        st.warning("⚠️ No se encontraron documentos con versiones registradas.")
                else:
                    st.error(f"❌ Error al obtener las versiones: {res.status_code}")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")

        st.button("⬅ Volver al panel principal", on_click=lambda: cambiar_vista("dashboard"))

        st.markdown('</div>', unsafe_allow_html=True)

        # --- FOOTER ---
        st.markdown("""
        <div class="footer">
            © 2025 Gestor Documental | Versiones Vigentes
        </div>
        """, unsafe_allow_html=True)
