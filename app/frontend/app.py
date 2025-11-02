import streamlit as st
from login import login_page
from register import register_page
from forgot_password import forgot_password_page
from reset_password import reset_password_page
from documentos import documentos_page
from versiones import versiones_page
from historial import historial_page
from dashboard import dashboard_page

# --- Configuración general ---
st.set_page_config(page_title="Gestor Documental", layout="wide")

# --- Estado de sesión (control de navegación y usuario) ---
if "vista" not in st.session_state:
    st.session_state.vista = "login"
if "token" not in st.session_state:
    st.session_state.token = None
if "usuario_nombre" not in st.session_state:
    st.session_state.usuario_nombre = None


# --- Función para cambiar de vista ---
def cambiar_vista(vista: str):
    st.session_state.vista = vista
    st.rerun()  # reemplaza experimental_rerun() (deprecated en nuevas versiones)


# --- Router principal ---
vista = st.session_state.vista

if vista == "login":
    login_page(cambiar_vista)

elif vista == "register":
    register_page(cambiar_vista)

elif vista == "forgot_password":
    forgot_password_page(cambiar_vista)

elif vista == "reset_password":
    reset_password_page(cambiar_vista)

elif vista == "dashboard":
    dashboard_page(cambiar_vista)
elif vista == "documentos":
    documentos_page(cambiar_vista)

elif vista == "versiones":
    versiones_page(cambiar_vista)

elif vista == "historial":
    historial_page(cambiar_vista)

else:
    st.error("❌ Página no encontrada o vista inválida.")
    st.write("Valor de vista:", vista)

