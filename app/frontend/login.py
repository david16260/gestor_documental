# login.py
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

def login_page(cambiar_vista):
    """Pantalla de inicio de sesión con estética tipo Dashboard, fondo blanco y botones verdes claros."""

    # --- Estilos generales ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background-color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Contenedor principal del login */
        .login-container {
            max-width: 420px;
            margin: 120px auto;
            background: #ffffff;
            border-radius: 16px;
            padding: 45px 35px;
            box-shadow: 0 4px 20px rgba(102, 187, 106, 0.25);
            text-align: center;
            border: 1px solid #c8e6c9;
        }

        /* Título */
        h2 {
            color: #66bb6a !important;
            font-weight: 800 !important;
            font-size: 36px !important;
            margin-bottom: 10px !important;
        }

        p.subtitle {
            color: #81c784 !important;
            font-size: 18px !important;
            font-weight: 500 !important;
            margin-bottom: 35px !important;
        }

        /* Inputs */
        .stTextInput > div > div > input {
            border-radius: 10px !important;
            border: 1px solid #c8e6c9 !important;
            padding: 12px 14px !important;
            font-size: 15px !important;
            transition: all 0.25s ease !important;
        }
        .stTextInput > div > div > input:focus {
            border: 1px solid #81c784 !important;
            box-shadow: 0 0 0 3px rgba(129,199,132,0.2) !important;
        }

        /* Botón principal */
        .stFormSubmitButton > button {
            width: 100% !important;
            height: 52px !important;
            border-radius: 10px !important;
            border: none !important;
            background: linear-gradient(135deg, #dcedc8 0%, #c5e1a5 100%) !important;
            color: #2e7d32 !important;
            font-weight: 800 !important;
            font-size: 18px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            letter-spacing: 0.5px !important;
        }
        .stFormSubmitButton > button:hover {
            background: linear-gradient(135deg, #c5e1a5 0%, #aed581 100%) !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102,187,106,0.3) !important;
        }

        /* Botones secundarios */
        div[data-testid="stButton"] > button {
            border-radius: 10px !important;
            height: 45px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            border: 1px solid #c8e6c9 !important;
            color: #388e3c !important;
            background: #f1f8e9 !important;
            transition: all 0.25s ease !important;
        }
        div[data-testid="stButton"] > button:hover {
            background: #dcedc8 !important;
            box-shadow: 0 3px 10px rgba(102,187,106,0.2) !important;
            transform: translateY(-1px);
        }

        /* Footer simple */
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #81c784;
            font-size: 13px;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Contenido del Login ---
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h2>🔒 Iniciar Sesión</h2>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Accede a tu cuenta del Gestor Documental</p>', unsafe_allow_html=True)

    with st.form("login-form"):
        email = st.text_input("Correo electrónico", placeholder="usuario@correo.com")
        password = st.text_input("Contraseña", type="password")
        login_btn = st.form_submit_button("Iniciar sesión")

    if login_btn:
        if not email or not password:
            st.error("Por favor, completa todos los campos.")
        else:
            form_data = {"username": email, "password": password}
            try:
                resp = requests.post(f"{API_BASE}/auth/login", data=form_data)
                data = resp.json()
                if resp.ok:
                    st.session_state.token = data["access_token"]
                    st.session_state.usuario_nombre = data.get("usuario", email.split("@")[0])
                    st.success(f"✅ Bienvenido, {st.session_state.usuario_nombre}.")
                    cambiar_vista("dashboard")
                else:
                    st.error(data.get("detail", "Error al iniciar sesión."))
            except requests.exceptions.ConnectionError:
                st.error(f"❌ No se pudo conectar con la API en {API_BASE}.")
            except Exception as err:
                st.error(f"❌ Error inesperado: {err}")

    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Crear cuenta", use_container_width=True):
            cambiar_vista("register")
    with col2:
        if st.button("❓ Olvidé mi contraseña", use_container_width=True):
            cambiar_vista("forgot_password")

    st.markdown('<div class="footer">© 2025 Gestor Documental</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
