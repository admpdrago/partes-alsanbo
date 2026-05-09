import streamlit as st
from fpdf import FPDF
from datetime import datetime, time, timedelta
import os

# --- CONFIGURACIÓN Y LISTA DE MATERIALES ---
# Aquí puedes añadir o quitar los materiales que más uses
MATERIALES_COMUNES = [
    "Selecciona un material...", 
    "Cable 1.5mm", 
    "Cable 2.5mm", 
    "Tubo Corrugado 20mm", 
    "Caja de registro",
    "Mecanismo interruptor",
    "Mecanismo enchufe",
    "Taco 6mm",
    "Tornillería",
    "Otro (Escribir manualmente...)"
]

st.set_page_config(page_title="Gestor de Partes", page_icon="🛠️")

def calcular_duracion(inicio, fin):
    hoy = datetime.today()
    dt_inicio = datetime.combine(hoy, inicio)
    dt_fin = datetime.combine(hoy, fin)
    if dt_fin < dt_inicio: dt_fin += timedelta(days=1)
    return round((dt_fin - dt_inicio).total_seconds() / 3600, 2)

# Mostrar logo en la web si existe
if os.path.exists("logo.png"):
    st.image("logo.png", width=120)

st.title("🛠️ Parte de Trabajo")

# --- FORMULARIO ---
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

# --- MATERIALES CON DESPLEGABLE ---
st.subheader("📦 Materiales")
if 'lista_mat' not in st.session_state:
    st.session_state.lista_mat = []

seleccion = st.selectbox("Elegir material común", MATERIALES_COMUNES)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    cant = st.number_input("Cant.", min_value=0.0, step=0.1, key="c")
with col2:
    unid = st.text_input("Unidad", value="uds", key="u")
with col3:
    # Si elige "Otro", dejamos que escriba. Si no, ponemos lo del desplegable.
    if seleccion == "Otro (Escribir manualmente...)":
        desc = st.text_input("Descripción", placeholder="Escribe el material...", key="m")
    elif seleccion != "Selecciona un material...":
        desc = st.text_input("Descripción", value=seleccion, key="m_select")
    else:
        desc = st.text_input("Descripción", placeholder="Selecciona o escribe", key="m_empty")

if st.button("➕ Añadir a la lista"):
    if desc and desc != "Selecciona un material...":
        st.session_state.lista_mat.append({"cantidad": cant, "unidad": unid, "material": desc})
    else:
        st.error("Debes indicar un material")

if st.session_state.lista_mat:
    st.table(st.session_state.lista_mat)
    if st.button("🗑️ Borrar lista"):
        st.session_state.lista_mat = []

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
        # Nombre de archivo dinámico para que se ordenen solos
        nombre_archivo = f"Parte_{fecha}_{cliente.replace(' ', '_')}.pdf"
        st.download_button("⬇️ Descargar y Guardar en Descargas", data=pdf_out, file_name=nombre_archivo)
    else:
        st.warning("Pon el nombre del cliente")