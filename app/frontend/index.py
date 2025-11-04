import streamlit as st

st.set_page_config(page_title="Inicio | Gestor Documental", layout="centered")

# --- Estilos personalizados ---
st.markdown("""
<style>
    body {
        background-color: #f8f9fa;
        font-family: Arial, sans-serif;
        padding-top: 80px;
    }
    .container {
        max-width: 600px;
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.1);
        margin: auto;
        text-align: center;
    }
    a {
        color: #0d6efd;
        text-decoration: none;
        font-weight: bold;
    }
    a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# --- Contenido principal ---
with st.container():
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown("<h2>Bienvenido al sistema de gestión documental</h2>", unsafe_allow_html=True)
    st.markdown("<p>Desde aquí podrás subir, consultar y gestionar tus documentos.</p>", unsafe_allow_html=True)
    st.markdown('<a href="/docs">Ver API Docs</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
