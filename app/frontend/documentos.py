import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"


def documentos_page(cambiar_vista):
    """Pantalla para subir documentos luego del login."""

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
            max-width: 700px;
            border: 1px solid #c8e6c9;
            margin-left: auto;
            margin-right: auto;
            transition: all 0.4s ease-in-out;
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

        /* Colores para botones de acciones */
        div[data-testid="stButton"]:nth-of-type(1) button {
            background: linear-gradient(135deg, #4caf50, #388e3c);
        }
        div[data-testid="stButton"]:nth-of-type(2) button {
            background: linear-gradient(135deg, #ffa726, #fb8c00);
        }
        div[data-testid="stButton"]:nth-of-type(3) button {
            background: linear-gradient(135deg, #f44336, #e53935);
        }
        
        /* Estilos para la vista previa del archivo */
        .file-preview {
            background: #f1f8e9;
            border: 2px solid #81c784;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .preview-title {
            color: #2e7d32;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .preview-item {
            background: white;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid #66bb6a;
        }
        
        .preview-label {
            color: #558b2f;
            font-weight: 600;
            font-size: 14px;
        }
        
        .preview-value {
            color: #2e7d32;
            font-size: 16px;
            margin-top: 4px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    st.markdown(f"""
    <div class="header">
        <div>👤 {usuario} | Subida de documentos</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

    # --- FORMULARIO PRINCIPAL ---
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.title("📁 Subir nuevo documento")

    # Selector de tipo de subida
    tipo_subida = st.radio("Método de carga:", ["Desde archivo", "Desde URL"])

    # --- Subida desde archivo ---
    if tipo_subida == "Desde archivo":
        archivo = st.file_uploader(
            "📄 Selecciona un archivo",
            type=["pdf", "docx", "xlsx", "txt", "png", "jpg"]
        )

        nombre = ""
        extension = ""

        if archivo:
            nombre = archivo.name.split(".")[0]
            extension = archivo.name.split(".")[-1]
            st.info(f"📌 Nombre detectado: **{nombre}**")
            st.info(f"📎 Extensión detectada: **.{extension}**")

        version = st.text_input("🔢 Versión", "1.0", key="version_archivo")
        categoria = st.selectbox("🏷️ Categoría", ["Administrativa", "Contable", "Otro"], key="categoria_archivo")

        if st.button("📤 Subir Documento"):
            if not archivo:
                st.warning("⚠️ Debes seleccionar un archivo para subir.")
            else:
                try:
                    tamano_bytes = archivo.size
                    tamano_kb = round(tamano_bytes / 1024, 2)
                    tamano_mb = round(tamano_bytes / (1024 * 1024), 2)
                    
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    files = {"file": (archivo.name, archivo.getvalue())}
                    data = {
                        "nombre": nombre,
                        "version": version,
                        "categoria": categoria,
                        "extension": extension,
                    }
                    resp = requests.post(f"{API_BASE}/documentos/upload", files=files, data=data, headers=headers)

                    if resp.ok:
                        st.success("✅ Documento subido correctamente.")
                        
                        # Mostrar información unificada después de subir
                        st.markdown(f"""
                        <div class="file-preview">
                            <div class="preview-title">📋 Información del Documento Subido</div>
                            <div class="preview-item">
                                <div class="preview-label">📌 Nombre del archivo</div>
                                <div class="preview-value">{nombre}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📎 Extensión</div>
                                <div class="preview-value">.{extension}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📏 Tamaño</div>
                                <div class="preview-value">{tamano_kb} KB ({tamano_mb} MB)</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📄 Nombre completo</div>
                                <div class="preview-value">{archivo.name}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🏷️ Clasificación</div>
                                <div class="preview-value">{categoria}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🔢 Versión</div>
                                <div class="preview-value">{version}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(resp.json().get("detail", "Error al subir el documento."))
                except Exception as e:
                    st.error(f"❌ Error de conexión: {e}")


    # --- Subida desde URL ---
    else:
        url = st.text_input("🌐 URL del documento", placeholder="https://...")

        nombre = ""
        extension = ""

        # Si el usuario escribe una URL válida, se obtiene el nombre y extensión automáticamente
        if url and "." in url.split("/")[-1]:
            archivo_nombre = url.split("/")[-1]
            nombre = archivo_nombre.rsplit(".", 1)[0]
            extension = archivo_nombre.rsplit(".", 1)[1]
            st.info(f"📌 Nombre detectado: **{nombre}**")
            st.info(f"📎 Extensión detectada: **.{extension}**")

        version = st.text_input("🔢 Versión", "1.0", key="version_url")
        categoria = st.selectbox("🏷️ Categoría", ["Administrativa", "Contable", "Otro"], key="categoria_url")

        # ✅ Ahora el botón de subir URL está dentro del bloque correcto
        if st.button("🌍 Subir desde URL"):
            if not url:
                st.warning("⚠️ Debes ingresar la URL del documento.")
            else:
                headers = {
                    "Authorization": f"Bearer {st.session_state.token}",
                    "Content-Type": "application/json"
                }
                payload = {"url": url, "version": version, "categoria": categoria}
                try:
                    resp = requests.post(f"{API_BASE}/documentos/desde-url", json=payload, headers=headers)

                    if resp.ok:
                        data = resp.json()
                        doc = data.get("documento", {})
                        extra = data.get("metadatos_extra", {})

                        st.success(f"✅ {data['mensaje']}")
                        
                        # Mostrar información unificada después de subir
                        st.markdown(f"""
                        <div class="file-preview">
                            <div class="preview-title">📋 Información del Documento Subido</div>
                            <div class="preview-item">
                                <div class="preview-label">🆔 ID del Documento</div>
                                <div class="preview-value">{doc.get('id')}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📌 Nombre</div>
                                <div class="preview-value">{doc.get('nombre')}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📎 Extensión</div>
                                <div class="preview-value">{doc.get('extension')}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📏 Tamaño</div>
                                <div class="preview-value">{doc.get('tamano_kb')} KB</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🏷️ Clasificación</div>
                                <div class="preview-value">{categoria}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🔢 Versión</div>
                                <div class="preview-value">{version}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📁 Ruta de guardado</div>
                                <div class="preview-value" style="word-break: break-all; font-family: monospace;">{doc.get("ruta_guardado")}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🔄 Duplicado</div>
                                <div class="preview-value">{"Sí" if doc.get('duplicado') else "No"}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("### 🧩 Metadatos adicionales")
                        st.json(extra)
                    else:
                        st.error(resp.json().get("detail", "No se pudo procesar la URL"))
                except Exception as e:
                    st.error(f"❌ Error de conexión: {e}")

    # --- BOTÓN DE VOLVER ---
    if st.button("⬅ Volver "):
        cambiar_vista("dashboard")