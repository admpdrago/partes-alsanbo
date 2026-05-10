import streamlit as st
from fpdf import FPDF
from datetime import datetime, time, timedelta
import os
import sqlite3
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión de Partes Pro", page_icon="🗄️", layout="wide")

# Inicializar Base de Datos
def crear_db():
    conn = sqlite3.connect('gestion_trabajos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS partes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  cliente TEXT, fecha TEXT, h_inicio TEXT, h_fin TEXT, 
                  total_h REAL, tareas TEXT, materiales TEXT)''')
    conn.commit()
    conn.close()

crear_db()

# Inicializar materiales en sesión
if 'mis_materiales' not in st.session_state:
    st.session_state.mis_materiales = ["Selecciona...", "Cable 1.5mm", "Cable 2.5mm", "Tubo Corrugado 20mm", "Otro..."]
if 'lista_mat_actual' not in st.session_state:
    st.session_state.lista_mat_actual = []

# --- FUNCIONES ---
def calcular_duracion(inicio, fin):
    hoy = datetime.today()
    dt_inicio = datetime.combine(hoy, inicio)
    dt_fin = datetime.combine(hoy, fin)
    if dt_fin < dt_inicio: dt_fin += timedelta(days=1)
    return round((dt_fin - dt_inicio).total_seconds() / 3600, 2)

def guardar_en_db(cliente, fecha, inicio, fin, total, tareas, materiales):
    conn = sqlite3.connect('gestion_trabajos.db')
    c = conn.cursor()
    c.execute("INSERT INTO partes (cliente, fecha, h_inicio, h_fin, total_h, tareas, materiales) VALUES (?,?,?,?,?,?,?)",
              (cliente, str(fecha), str(inicio), str(fin), total, tareas, str(materiales)))
    conn.commit()
    conn.close()

# --- INTERFAZ ---
st.sidebar.title("Menú")
choice = st.sidebar.radio("Ir a:", ["📝 Nuevo Parte", "🗄️ Historial"])

if choice == "📝 Nuevo Parte":
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    st.title("Nuevo Parte de Trabajo")

    with st.expander("1. Datos Generales", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Cliente / Obra")
            fecha = st.date_input("Fecha", datetime.now())
        with col2:
            h_inicio = st.time_input("Inicio", time(8, 0))
            h_fin = st.time_input("Fin", time(18, 0))
            total_h = calcular_duracion(h_inicio, h_fin)
            st.write(f"**Total horas:** {total_h}")
        
        tareas = st.text_area("Descripción del trabajo")

    with st.expander("2. Materiales"):
        seleccion = st.selectbox("Elegir de la lista", st.session_state.mis_materiales)
        c1, c2, c3 = st.columns([1,1,2])
        with c1: cant = st.number_input("Cant.", min_value=0.0, step=0.1)
        with c2: unid = st.text_input("Unidad", value="uds")
        with c3:
            if seleccion == "Otro...":
                desc = st.text_input("Nombre del material")
            else:
                desc = seleccion
        
        if st.button("➕ Añadir Material"):
            if desc and desc != "Selecciona...":
                st.session_state.lista_mat_actual.append({"cantidad": cant, "unidad": unid, "material": desc})
                if desc not in st.session_state.mis_materiales:
                    st.session_state.mis_materiales.insert(-1, desc)
                st.rerun()

        if st.session_state.lista_mat_actual:
            st.table(st.session_state.lista_mat_actual)

    if st.button("💾 GUARDAR TODO EN BASE DE DATOS"):
        if cliente:
            guardar_en_db(cliente, fecha, h_inicio, h_fin, total_h, tareas, st.session_state.lista_mat_actual)
            st.success("¡Parte guardado con éxito! Puedes verlo en el Historial.")
            st.session_state.lista_mat_actual = [] # Limpiar para el siguiente
        else:
            st.error("El nombre del cliente es obligatorio")

elif choice == "🗄️ Historial":
    st.title("Historial de Partes")
    conn = sqlite3.connect('gestion_trabajos.db')
    df = pd.read_sql_query("SELECT * FROM partes ORDER BY id DESC", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df[['id', 'cliente', 'fecha', 'total_h', 'tareas']], use_container_width=True)
    else:
        st.info("No hay partes guardados todavía.")