import streamlit as st
from fpdf import FPDF
from datetime import datetime, time, timedelta
import os

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Gestor de Partes Inteligente", page_icon="🛠️")

# Inicializamos la lista de materiales comunes en la memoria de la sesión
if 'mis_materiales' not in st.session_state:
    st.session_state.mis_materiales = [
        "Selecciona...", 
        "Cable 1.5mm", 
        "Cable 2.5mm", 
        "Tubo Corrugado 20mm", 
        "Otro (Escribir manualmente...)"
    ]

if 'lista_mat' not in st.session_state:
    st.session_state.lista_mat = []

def calcular_duracion(inicio, fin):
    hoy = datetime.today()
    dt_inicio = datetime.combine(hoy, inicio)
    dt_fin = datetime.combine(hoy, fin)
    if dt_fin < dt_inicio: dt_fin += timedelta(days=1)
    return round((dt_fin - dt_inicio).total_seconds() / 3600, 2)

if os.path.exists("logo.png"):
    st.image("logo.png", width=120)

st.title("🛠️ Parte de Trabajo")

# --- FORMULARIO DATOS ---
with st.expander("Datos del Trabajo", expanded=True):
    cliente = st.text_input("Cliente / Obra")
    fecha = st.date_input("Fecha", datetime.now())
    c1, c2 = st.columns(2)
    with c1: h_inicio = st.time_input("Inicio", time(8, 0))
    with c2: h_fin = st.time_input("Fin", time(18, 0))
    total_h = calcular_duracion(h_inicio, h_fin)
    st.info(f"Horas: {total_h}")
    tareas = st.text_area("Descripción del trabajo")

st.divider()

# --- MATERIALES CON AUTO-APRENDIZAJE ---
st.subheader("📦 Materiales")

seleccion = st.selectbox("Materiales guardados", st.session_state.mis_materiales)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    cant = st.number_input("Cant.", min_value=0.0, step=0.1, key="c")
with col2:
    unid = st.text_input("Unidad", value="uds", key="u")
with col3:
    # Lógica para escribir manual o usar el selector
    if seleccion == "Otro (Escribir manualmente...)":
        desc = st.text_input("Escribe el nuevo material", key="m_nuevo")
    elif seleccion != "Selecciona...":
        desc = st.text_input("Confirmar material", value=seleccion, key="m_conf")
    else:
        desc = ""

if st.button("➕ Añadir y Guardar Material"):
    if desc and desc != "Selecciona...":
        # 1. Añadir a la lista del parte actual
        st.session_state.lista_mat.append({"cantidad": cant, "unidad": unid, "material": desc})
        
        # 2. APRENDIZAJE: Si no estaba en el desplegable, lo añadimos para siempre (en esta sesión)
        if desc not in st.session_state.mis_materiales:
            # Insertamos antes de la opción "Otro"
            st.session_state.mis_materiales.insert(-1, desc)
            st.success(f"'{desc}' guardado en el desplegable")
        
        st.rerun() # Refrescamos para limpiar campos y actualizar lista
    else:
        st.error("Escribe o selecciona un material válido")

if st.session_state.lista_mat:
    st.table(st.session_state.lista_mat)
    if st.button("🗑️ Vaciar lista actual"):
        st.session_state.lista_mat = []
        st.rerun()

# --- GENERAR PDF ---
def crear_pdf(cliente, fecha, h_inicio, h_fin, h_total, tareas, materiales):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 40)
        pdf.ln(25)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "PARTE DE TRABAJO", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(30, 10, "Cliente:", 0); pdf.set_font("Arial", '', 12); pdf.cell(0, 10, str(cliente), ln=True)
    pdf.set_font("Arial", 'B', 12); pdf.cell(30, 10, "Fecha:", 0); pdf.set_font("Arial", '', 12); pdf.cell(0, 10, str(fecha), ln=True)
    pdf.set_font("Arial", 'B', 12); pdf.cell(30, 10, "Horario:", 0); pdf.set_font("Arial", '', 12); pdf.cell(0, 10, f"{h_inicio} a {h_fin} ({h_total}h)", ln=True)
    
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Tareas realizadas:", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, tareas)
    
    if materiales:
        pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Materiales:", ln=True)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(25, 8, "Cant.", 1); pdf.cell(35, 8, "Unidad", 1); pdf.cell(0, 8, "Descripcion", 1, ln=True)
        pdf.set_font("Arial", '', 10)
        for m in materiales:
            pdf.cell(25, 8, str(m['cantidad']), 1); pdf.cell(35, 8, m['unidad'], 1); pdf.cell(0, 8, m['material'], 1, ln=True)
    
    pdf.ln(20); pdf.set_font("Arial", 'I', 10); pdf.cell(0, 10, "Firma del tecnico / Conformidad", ln=True)
    pdf.line(10, pdf.get_y(), 60, pdf.get_y())
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("💾 GENERAR PDF"):
    if cliente:
        pdf_out = crear_pdf(cliente, fecha, h_inicio, h_fin, total_h, tareas, st.session_state.lista_mat)
        nombre_archivo = f"Parte_{fecha}_{cliente.replace(' ', '_')}.pdf"
        st.download_button("⬇️ Descargar PDF", data=pdf_out, file_name=nombre_archivo)
    else:
        st.warning("Escribe el nombre del cliente")