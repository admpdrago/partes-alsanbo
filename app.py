import streamlit as st
from fpdf import FPDF
from datetime import datetime, time, timedelta
import os

# Configuración de la página
st.set_page_config(page_title="Gestor de Partes de Trabajo", page_icon="🛠️")

# --- FUNCIÓN PARA CALCULAR TIEMPO ---
def calcular_duracion(inicio, fin):
    hoy = datetime.today()
    dt_inicio = datetime.combine(hoy, inicio)
    dt_fin = datetime.combine(hoy, fin)
    if dt_fin < dt_inicio:
        dt_fin += timedelta(days=1)
    diferencia = dt_fin - dt_inicio
    return round(diferencia.total_seconds() / 3600, 2)

# Mostrar logo en la web si existe
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)

st.title("🛠️ Registro de Trabajo")

# --- FORMULARIO PRINCIPAL ---
with st.container():
    cliente = st.text_input("Nombre del Cliente / Obra")
    fecha = st.date_input("Fecha", datetime.now())
    
    st.subheader("⏱️ Registro de Tiempo")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        hora_inicio = st.time_input("Hora de Inicio", time(8, 0))
    with col_t2:
        hora_fin = st.time_input("Hora de Fin", time(18, 0))
    
    total_h = calcular_duracion(hora_inicio, hora_fin)
    st.info(f"Tiempo total calculado: **{total_h} horas**")
    
    tareas = st.text_area("Descripción de las tareas realizadas")

st.divider()

# --- GESTIÓN DE MATERIALES (OPCIONAL) ---
st.subheader("📦 Materiales utilizados (Opcional)")
if 'lista_mat' not in st.session_state:
    st.session_state.lista_mat = []

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    cant = st.number_input("Cant.", min_value=0.0, step=0.1, key="c")
with c2:
    unid = st.text_input("Unidad", placeholder="uds, m...", key="u")
with c3:
    desc = st.text_input("Descripción", placeholder="Nombre del material", key="m")

if st.button("➕ Añadir Material"):
    if desc:
        st.session_state.lista_mat.append({"cantidad": cant, "unidad": unid, "material": desc})
    else:
        st.error("Escribe la descripción del material")

if st.session_state.lista_mat:
    st.table(st.session_state.lista_mat)
    if st.button("🗑️ Limpiar lista de materiales"):
        st.session_state.lista_mat = []

# --- GENERACIÓN DE PDF ---
def crear_pdf(cliente, fecha, h_inicio, h_fin, h_total, tareas, materiales):
    pdf = FPDF()
    pdf.add_page()
    
    # Lógica del Logo
    if os.path.exists("logo.png"):
        # Insertar imagen: x=10, y=8, ancho=30
        pdf.image("logo.png", 10, 8, 30)
        pdf.ln(25) 
    else:
        pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "PARTE DE TRABAJO", ln=True, align='R' if os.path.exists("logo.png") else 'C')
    pdf.ln(10)
    
    # Datos generales
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(30, 10, "Cliente:", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(cliente), ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(30, 10, "Fecha:", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(fecha), ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(30, 10, "Horario:", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"De {h_inicio} a {h_fin} (Total: {h_total} horas)", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Descripción de los trabajos:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, tareas)
    
    # Solo mostrar tabla de materiales si hay alguno
    if materiales:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Materiales empleados:", ln=True)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(25, 8, "Cant.", 1)
        pdf.cell(35, 8, "Unidad", 1)
        pdf.cell(0, 8, "Descripción", 1, ln=True)
        
        pdf.set_font("Arial", '', 10)
        for m in materiales:
            pdf.cell(25, 8, str(m['cantidad']), 1)
            pdf.cell(35, 8, m['unidad'], 1)
            pdf.cell(0, 8, m['material'], 1, ln=True)
    
    # Pie de página / Firma
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Firma del técnico / Conformidad", ln=True)
    pdf.line(10, pdf.get_y(), 60, pdf.get_y())
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("💾 GENERAR Y DESCARGAR PDF"):
    if cliente: # Ahora solo es obligatorio el cliente
        pdf_out = crear_pdf(cliente, fecha, hora_inicio, hora_fin, total_h, tareas, st.session_state.lista_mat)
        st.download_button("⬇️ Descargar PDF", data=pdf_out, file_name=f"Parte_{cliente}.pdf")
    else:
        st.warning("Por favor, introduce al menos el nombre del cliente.")