# register.py
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

def register_page(cambiar_vista):
    """Pantalla de registro con estilo verde y fondo blanco tipo dashboard."""
    
    # --- Estilos personalizados ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background-color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Contenedor principal */
        .register-container {
            max-width: 450px;
            margin: 120px auto;
            background: #ffffff;
            border-radius: 16px;
            padding: 45px 35px;
            box-shadow: 0 4px 20px rgba(102, 187, 106, 0.25);
            text-align: center;
            border: 1px solid #c8e6c9;
        }

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

        /* Botón volver */
        div[data-testid="stButton"] > button {
            border-radius: 10px !important;
            height: 45px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            border: 1px solid #c8e6c9 !important;
            color: #388e3c !important;
            background: #f1f8e9 !important;
            transition: all 0.25s ease !important;
            width: 100% !important;
        }
        div[data-testid="stButton"] > button:hover {
            background: #dcedc8 !important;
            box-shadow: 0 3px 10px rgba(102,187,106,0.2) !important;
            transform: translateY(-1px);
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: #81c784;
            font-size: 13px;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Contenido visual ---
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    st.markdown("<h2>📝 Crear Cuenta</h2>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Regístrate en el Gestor Documental</p>', unsafe_allow_html=True)

    with st.form("registerForm"):
        nombre = st.text_input("Nombre completo", placeholder="Juan Pérez")
        email = st.text_input("Correo electrónico", placeholder="usuario@correo.com")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Registrarse")

    if submit:
        if not nombre or not email or not password:
            st.error("Por favor, completa todos los campos.")
        else:
            form_data = {"nombre": nombre, "email": email, "password": password}
            try:
                res = requests.post(f"{API_BASE}/auth/register", data=form_data)
                if res.ok:
                    st.success("✅ Usuario registrado correctamente")
                    st.toast("Usuario creado, redirigiendo al inicio de sesión...", icon="✅")
                    st.session_state.vista = "login"
                    st.rerun()
                else:
                    error = res.json()
                    st.error(error.get("detail", "Error al registrarse"))
            except requests.exceptions.ConnectionError:
                st.error("❌ No se pudo conectar con la API.")
            except Exception as err:
                st.error(f"❌ Error inesperado: {err}")

    # --- Botón volver ---
    if st.button("⬅ Volver al inicio de sesión"):
        cambiar_vista("login")

    st.markdown('<div class="footer">© 2025 Gestor Documental</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
