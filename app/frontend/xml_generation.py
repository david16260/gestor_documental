import streamlit as st
import requests
import json

API_BASE = "http://127.0.0.1:8000"


def xml_generation_page(cambiar_vista):
    """Pantalla para generar archivos XML de documentos."""

    # --- Validar sesión ---
    if "token" not in st.session_state or not st.session_state.token:
        st.warning("🔒 No has iniciado sesión.")
        st.stop()

    usuario = st.session_state.get("usuario_nombre", "Desconocido")

    # --- Estilos visuales ---
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #e3f2fd, #bbdefb);
            font-family: 'Segoe UI', Tahoma, sans-serif;
        }

        .header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(135deg, #1976d2, #2196f3);
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
            max-width: 900px;
            border: 1px solid #bbdefb;
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
            background: linear-gradient(135deg, #2196f3, #1976d2);
        }
        div[data-testid="stButton"]:nth-of-type(2) button {
            background: linear-gradient(135deg, #42a5f5, #1e88e5);
        }
        div[data-testid="stButton"]:nth-of-type(3) button {
            background: linear-gradient(135deg, #f44336, #e53935);
        }
        
        /* Estilos para la vista previa del XML */
        .xml-preview {
            background: #e3f2fd;
            border: 2px solid #64b5f6;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .preview-title {
            color: #1976d2;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .preview-item {
            background: white;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid #42a5f5;
        }
        
        .preview-label {
            color: #1565c0;
            font-weight: 600;
            font-size: 14px;
        }
        
        .preview-value {
            color: #1976d2;
            font-size: 16px;
            margin-top: 4px;
        }

        .info-box {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            color: #e65100;
        }

        .success-box {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            color: #2e7d32;
        }

        .metadata-box {
            background: #f3e5f5;
            border: 2px solid #ba68c8;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }

        .metadata-title {
            color: #7b1fa2;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 12px;
        }

        .xml-code {
            background: #263238;
            color: #aed581;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            max-height: 400px;
            overflow-y: auto;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-card {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #1976d2;
        }

        .stat-label {
            font-size: 14px;
            color: #1565c0;
            margin-top: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    st.markdown(f"""
    <div class="header">
        <div>📄 {usuario} | Generación de XML según TRD</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

    # --- FORMULARIO PRINCIPAL ---
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.title("📝 Generación de Comprobantes XML")

    # Información sobre XML y estándar TRD
    st.markdown("""
    <div class="info-box">
        <strong>ℹ️ Información del Sistema:</strong><br>
        Los archivos XML generados cumplen con el estándar de <strong>DocumentoIndizado</strong> 
        para gestión documental según Tablas de Retención Documental (TRD).<br><br>
        <strong>Metadatos incluidos:</strong> ID, Tipología Documental, Fechas (Creación/Incorporación), 
        Hash MD5, Orden en Expediente, Paginación, Formato y Tamaño.
    </div>
    """, unsafe_allow_html=True)

    # Selector de tipo de generación
    tipo_generacion = st.radio(
        "Tipo de generación:", 
        ["XML Individual (un documento)", "XML Expediente Completo (todos los documentos)"]
    )

    # --- Generación XML Individual ---
    if tipo_generacion == "XML Individual (un documento)":
        st.markdown("### 📄 Generar XML de un documento específico")
        
        # Obtener lista de documentos del usuario
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            resp_docs = requests.get(f"{API_BASE}/documentos/", headers=headers)
            
            if resp_docs.ok:
                documentos = resp_docs.json()
                
                if not documentos:
                    st.warning("⚠️ No tienes documentos cargados en el sistema.")
                else:
                    # Crear lista de opciones para el selectbox
                    opciones_docs = [
                        f"ID: {doc['id']} - {doc['nombre']} v{doc['version']} ({doc['extension']})"
                        for doc in documentos
                    ]
                    
                    documento_seleccionado = st.selectbox(
                        "🔍 Selecciona el documento:",
                        opciones_docs
                    )
                    
                    # Extraer ID del documento seleccionado
                    doc_id = int(documento_seleccionado.split("ID: ")[1].split(" -")[0])
                    
                    # Mostrar información del documento seleccionado
                    doc_info = next((doc for doc in documentos if doc['id'] == doc_id), None)
                    if doc_info:
                        st.markdown(f"""
                        <div class="xml-preview">
                            <div class="preview-title">📋 Información del Documento</div>
                            <div class="preview-item">
                                <div class="preview-label">📌 Nombre</div>
                                <div class="preview-value">{doc_info['nombre']}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🔖 Extensión</div>
                                <div class="preview-value">.{doc_info['extension']}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">📦 Tamaño</div>
                                <div class="preview-value">{doc_info['tamano_kb']} KB</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🗓️ Fecha de creación</div>
                                <div class="preview-value">{doc_info.get('creado_en', 'N/A')}</div>
                            </div>
                            <div class="preview-item">
                                <div class="preview-label">🔐 Hash MD5</div>
                                <div class="preview-value" style="font-family: monospace; font-size: 12px;">{doc_info.get('hash_archivo', 'N/A')[:12]}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Metadatos TRD esperados
                    st.markdown("""
                    <div class="metadata-box">
                        <div class="metadata-title">📋 Metadatos TRD a incluir en el XML</div>
                        <ul style="color: #7b1fa2; font-size: 14px;">
                            <li><strong>Id:</strong> {usuario_id}{documento_id}TD (identificador único)</li>
                            <li><strong>NombreDocumento:</strong> Nombre sin extensión</li>
                            <li><strong>TipologíaDocumental:</strong> Detectada automáticamente (Acta, Certificación, Informe, etc.)</li>
                            <li><strong>FechaCreacionDocumento:</strong> Formato YYYYMMDD</li>
                            <li><strong>FechaIncorporacionExpediente:</strong> Fecha de registro en sistema</li>
                            <li><strong>ValorHuella:</strong> MD5 (primeros 12 caracteres en mayúsculas)</li>
                            <li><strong>FuncionResumen:</strong> MD5</li>
                            <li><strong>OrdenDocumentoExpediente:</strong> Posición secuencial</li>
                            <li><strong>PaginaInicio/PaginaFin:</strong> Rango de páginas</li>
                            <li><strong>Formato:</strong> PDF/A, DOCX, XLSX, JPEG, etc.</li>
                            <li><strong>Tamano:</strong> Tamaño en KB</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📥 Generar y Visualizar XML"):
                            with st.spinner("Generando XML con metadatos TRD..."):
                                try:
                                    resp = requests.get(
                                        f"{API_BASE}/xml/documento/{doc_id}",
                                        headers=headers
                                    )
                                    
                                    if resp.ok:
                                        data = resp.json()
                                        st.success("✅ XML generado exitosamente")
                                        
                                        st.markdown(f"""
                                        <div class="success-box">
                                            <strong>✓ Generación exitosa</strong><br>
                                            Ruta de guardado: <code>{data['ruta_xml']}</code><br>
                                            <small>El archivo incluye todos los metadatos según estándar TRD</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Mostrar preview del XML
                                        st.markdown("### 📝 Vista previa del XML generado:")
                                        st.code(data['xml_preview'], language='xml')
                                        
                                        # Explicación de campos
                                        with st.expander("ℹ️ Ver explicación de campos XML"):
                                            st.markdown("""
                                            **Campos del XML generado:**
                                            - **Id**: Identificador único compuesto por usuario_id + documento_id + 'TD'
                                            - **NombreDocumento**: Nombre del archivo sin extensión
                                            - **TipologíaDocumental**: Clasificación según TRD (Acta, Certificación, etc.)
                                            - **FechaCreacionDocumento**: Fecha original del documento
                                            - **FechaIncorporacionExpediente**: Fecha de carga al sistema
                                            - **ValorHuella**: Hash MD5 truncado a 12 caracteres
                                            - **FuncionResumen**: Algoritmo usado (MD5)
                                            - **OrdenDocumentoExpediente**: Orden secuencial
                                            - **PaginaInicio/PaginaFin**: Rango de páginas en expediente
                                            - **Formato**: Formato estandarizado (PDF/A, DOCX, etc.)
                                            - **Tamano**: Tamaño del archivo en KB
                                            """)
                                    else:
                                        st.error(f"❌ Error: {resp.json().get('detail', 'Error desconocido')}")
                                except Exception as e:
                                    st.error(f"❌ Error de conexión: {e}")
                    
                    with col2:
                        if st.button("💾 Descargar XML"):
                            with st.spinner("Preparando descarga..."):
                                try:
                                    resp = requests.get(
                                        f"{API_BASE}/xml/documento/{doc_id}/descargar",
                                        headers=headers
                                    )
                                    
                                    if resp.ok:
                                        # Crear botón de descarga
                                        st.download_button(
                                            label="⬇️ Descargar archivo XML",
                                            data=resp.content,
                                            file_name=f"documento_{doc_id}_comprobante.xml",
                                            mime="application/xml"
                                        )
                                        st.success("✅ XML listo para descargar")
                                    else:
                                        st.error("❌ Error al generar el XML")
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
            else:
                st.error("❌ No se pudo cargar la lista de documentos")
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")

    # --- Generación XML Expediente Completo ---
    else:
        st.markdown("### 📚 Generar XML del expediente completo")
        
        st.markdown("""
        <div class="info-box">
            <strong>📦 Expediente Completo:</strong><br>
            Esta opción genera un único archivo XML que contiene todos tus documentos 
            organizados secuencialmente con:<br>
            • Numeración de páginas automática (1 página ≈ 100KB)<br>
            • Orden secuencial de documentos<br>
            • Metadatos TRD completos para cada documento<br>
            • Estructura Root con múltiples DocumentoIndizado<br>
            • Namespace XSI para validación con schemas
        </div>
        """, unsafe_allow_html=True)
        
        # Obtener ID del usuario desde el token o session state
        usuario_id = st.session_state.get("usuario_id", 1)
        
        # Mostrar estadísticas antes de generar
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            resp_docs = requests.get(f"{API_BASE}/documentos/", headers=headers)
            
            if resp_docs.ok:
                documentos = resp_docs.json()
                total_docs = len(documentos)
                total_kb = sum(doc.get('tamano_kb', 0) for doc in documentos)
                total_mb = round(total_kb / 1024, 2)
                paginas_estimadas = max(1, int(total_kb / 100))
                
                st.markdown(f"""
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{total_docs}</div>
                        <div class="stat-label">Documentos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_mb}</div>
                        <div class="stat-label">MB Totales</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{paginas_estimadas}</div>
                        <div class="stat-label">Páginas Estimadas</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except:
            pass
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Generar Expediente XML"):
                with st.spinner("Generando expediente completo con metadatos TRD..."):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        resp = requests.get(
                            f"{API_BASE}/xml/expediente/usuario/{usuario_id}",
                            headers=headers
                        )
                        
                        if resp.ok:
                            data = resp.json()
                            st.success(f"✅ {data['mensaje']}")
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <strong>✓ Expediente generado exitosamente</strong><br>
                                Total de documentos incluidos: <strong>{data['total_documentos']}</strong><br>
                                <small>Cada documento incluye metadatos TRD completos según estándar</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Mostrar preview del XML (primeros 2000 caracteres)
                            st.markdown("### 📝 Vista previa del expediente XML:")
                            preview_xml = data['xml_preview']
                            if len(preview_xml) > 2000:
                                st.code(preview_xml[:2000] + "\n\n... (XML completo disponible en descarga)", language='xml')
                            else:
                                st.code(preview_xml, language='xml')
                            
                            # Información adicional
                            with st.expander("ℹ️ Estructura del expediente XML"):
                                st.markdown("""
                                **Estructura del expediente completo:**
                                ```xml
                                <Root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                    <DocumentoIndizado>
                                        <!-- Metadatos documento 1 -->
                                    </DocumentoIndizado>
                                    <DocumentoIndizado>
                                        <!-- Metadatos documento 2 -->
                                    </DocumentoIndizado>
                                    ...
                                </Root>
                                ```
                                
                                **Paginación automática:**
                                - Se calcula 1 página ≈ 100KB
                                - Páginas acumulativas para todo el expediente
                                - Ejemplo: Doc1 (300KB) = págs 1-3, Doc2 (200KB) = págs 4-5
                                """)
                        else:
                            st.error(f"❌ Error: {resp.json().get('detail', 'Error desconocido')}")
                    except Exception as e:
                        st.error(f"❌ Error de conexión: {e}")
        
        with col2:
            if st.button("💾 Descargar Expediente XML"):
                with st.spinner("Preparando descarga del expediente..."):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        resp = requests.get(
                            f"{API_BASE}/xml/expediente/usuario/{usuario_id}/descargar",
                            headers=headers
                        )
                        
                        if resp.ok:
                            # Crear botón de descarga
                            st.download_button(
                                label="⬇️ Descargar expediente completo",
                                data=resp.content,
                                file_name=f"expediente_usuario_{usuario_id}.xml",
                                mime="application/xml"
                            )
                            st.success("✅ Expediente listo para descargar")
                        else:
                            st.error("❌ Error al generar el expediente")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- Información adicional sobre TRD ---
    with st.expander("📚 ¿Qué es una Tabla de Retención Documental (TRD)?"):
        st.markdown("""
        ### Tabla de Retención Documental (TRD)
        
        Es un instrumento archivístico que establece:
        
        **🗂️ Series y Subseries Documentales:**
        - Administrativa (Actas, Resoluciones, Circulares)
        - Contabilidad (Comprobantes, Balances, Estados Financieros)
        - Contratación (Contratos, Solicitudes de Pago)
        - Gestión Documental (Informes, Oficios, Certificaciones)
        
        **📋 Tipologías Documentales detectadas automáticamente:**
        - Acta de Reunión
        - Certificación de Pago
        - Informe de Gestión
        - Comprobante Contable
        - Oficio
        - Balance y Estados
        - Resolución Interna
        - Circular
        - Solicitud de Pago
        - Contrato
        
        **🔐 Hash MD5:**
        - Garantiza la integridad del documento
        - Se trunca a 12 caracteres en mayúsculas
        - Permite verificar que el archivo no ha sido alterado
        
        **📄 Formatos soportados:**
        - PDF/A (archivable según ISO 19005)
        - DOCX, DOC (Microsoft Word)
        - XLSX, XLS (Microsoft Excel)
        - JPEG, PNG (Imágenes)
        - TXT (Texto plano)
        """)

    # --- BOTÓN DE VOLVER ---
    if st.button("⬅️ Volver"):
        cambiar_vista("dashboard")