import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

def reset_password_page(cambiar_vista):
    st.set_page_config(page_title="Restablecer contraseña | Gestor Documental", layout="centered")

    # --- Estilos personalizados ---
    st.markdown("""
    <style>
        body { background:#f8f9fa; font-family:Arial,sans-serif; padding-top:80px; }
        .container { 
            max-width:400px; 
            background:white; 
            border-radius:12px; 
            padding:25px; 
            box-shadow:0 0 12px rgba(0,0,0,0.1); 
            margin:auto; 
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Contenedor visual ---
    with st.container():
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown('<h4 class="text-center mb-3">🔑 Restablecer contraseña</h4>', unsafe_allow_html=True)

        # Prellenar token si está en session_state o en la URL
        token_default = st.session_state.get("reset_token", "")
        if not token_default:
            token_default = st.query_params.get("reset_token", [""])[0]

        with st.form("reset-form"):
            token = st.text_input("Token recibido", value=token_default)
            nueva_password = st.text_input("Nueva contraseña", type="password")
            enviar = st.form_submit_button("Restablecer contraseña")

        if enviar:
            form_data = {"token": token, "nueva_password": nueva_password}
            try:
                resp = requests.post(f"{API_BASE}/auth/reset-password", data=form_data)
                data = resp.json()
                if resp.ok:
                    st.success(f"✅ {data.get('mensaje', 'Contraseña restablecida correctamente')}")
                    st.session_state.reset_token = None
                    st.info("Redirigiendo al login...")
                    st.sleep(1.5)
                    cambiar_vista("login")  # 🔁 Regresa al login
                else:
                    st.error(f"❌ {data.get('detail', 'Error al restablecer contraseña')}")
            except Exception as err:
                st.error(f"❌ Error de conexión: {err}")

        if st.button("⬅ Volver al inicio de sesión"):
            cambiar_vista("login")

        st.markdown('</div>', unsafe_allow_html=True)
