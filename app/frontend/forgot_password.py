# forgot_password.py
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

def forgot_password_page(cambiar_vista):
    """Pantalla para recuperar la contraseña con estilo verde."""
    
    # --- Estilos personalizados ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background-color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Contenedor principal */
        .forgot-container {
            max-width: 450px;
            margin: 120px auto;
            background: #ffffff;
            border-radius: 16px;
            padding: 45px 35px;
            box-shadow: 0 4px 20px rgba(102, 187, 106, 0.25);
            text-align: center;
            border: 1px solid #c8e6c9;
        }

        h3 {
            color: #66bb6a !important;
            font-weight: 800 !important;
            font-size: 34px !important;
            margin-bottom: 15px !important;
        }

        p.subtitle {
            color: #81c784 !important;
            font-size: 17px !important;
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
    st.markdown('<div class="forgot-container">', unsafe_allow_html=True)
    st.markdown("<h3>🔑 Recuperar Contraseña</h3>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ingresa tu correo para recibir un enlace de recuperación</p>', unsafe_allow_html=True)

    with st.form("forgot-form"):
        email = st.text_input("Correo electrónico", placeholder="usuario@correo.com")
        enviar = st.form_submit_button("Enviar token de recuperación")

    if enviar and email:
        try:
            resp = requests.post(f"{API_BASE}/auth/forgot-password", json={"email": email})
            data = resp.json()

            if resp.ok:
                st.success("✅ Token generado correctamente. Verifica tu correo electrónico.")
                st.session_state.reset_token = data.get("reset_token")
                cambiar_vista("reset_password")
            else:
                st.error(f"❌ {data.get('detail', 'Error al generar token.')}")
        except requests.exceptions.ConnectionError:
            st.error("❌ No se pudo conectar con el servidor.")
        except Exception as err:
            st.error(f"❌ Error inesperado: {err}")

    if st.button("⬅ Volver al inicio de sesión"):
        cambiar_vista("login")

    st.markdown('<div class="footer">© 2025 Gestor Documental</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


