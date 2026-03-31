import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración inicial
st.set_page_config(layout="wide", page_title="SNAP - Monitor de Operaciones")

# --- CONEXIÓN A BASE DE DATOS ---
def get_data(query):
    try:
        conn = sqlite3.connect('gestion_snap_v5.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- ESTILOS CSS (Para replicar tu interfaz de Tkinter) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .header { background-color: #28a745; color: white; padding: 10px; text-align: center; border-radius: 5px; margin-bottom: 20px; }
    .card-novedad { background-color: #c0392b; color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-size: 0.9em; }
    .card-plan { border: 2px solid #28a745; background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .alerta-amarilla { border: 2px solid #FFFF00 !important; background-color: #fffff0; }
    .card-intervencion-blue { background-color: #3498db; color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    .card-intervencion-red { background-color: #c0392b; color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header"><h1>MONITOR DE OPERACIONES</h1><p style="text-align:right;">Created by Facundo Ramua</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.2, 3, 1.2])

# --- COLUMNA 1: NOVEDADES DEL PERSONAL ---
with col1:
    st.markdown("### ⚠️ NOVEDADES")
    novedades = get_data("SELECT nombre, novedad, fecha_inicio, fecha_fin FROM novedades")
    if not novedades.empty:
        for _, row in novedades.iterrows():
            st.markdown(f"""
                <div class="card-novedad">
                    <b>{row['nombre']}</b><br>{row['novedad']}<br>
                    <small>Del {row['fecha_inicio']} al {row['fecha_fin']}</small>
                </div>
            """, unsafe_allow_html=True)

# --- COLUMNA 2: PLANIFICACIÓN DEL DÍA ---
with col2:
    st.markdown(f"### PLANIFICACIÓN DEL DÍA ({datetime.now().strftime('%d/%m/%Y')})")
    plan = get_data("SELECT * FROM planificacion") # Ajusta el nombre de la tabla si es distinto
    if not plan.empty:
        for _, row in plan.iterrows():
            # TU REGLA: Si hay rango horario, borde amarillo
            clase_alerta = "alerta-amarilla" if "07:00" in str(row.get('horario', '')) else ""
            st.markdown(f"""
                <div class="card-plan {clase_alerta}">
                    <b style="color:#28a745;">{row.get('lugar', 'SITIO')}</b><br>
                    <b>RESPONSABLE:</b> {row.get('responsable', 'N/A')}<br>
                    <b>TAREAS:</b> {row.get('tareas', 'Sin tareas asignadas')}
                </div>
            """, unsafe_allow_html=True)

# --- COLUMNA 3: ÚLTIMAS INTERVENCIONES ---
with col3:
    st.markdown("### 📅 ÚLTIMAS INTERVENCIONES")
    intervenciones = get_data("SELECT lugar, motivo, fecha FROM intervenciones ORDER BY fecha DESC LIMIT 10")
    if not intervenciones.empty:
        for _, row in intervenciones.iterrows():
            # Lógica de color (azul para hoy, rojo para días atrás)
            es_hoy = row['fecha'] == datetime.now().strftime('%Y-%m-%d')
            clase_color = "card-intervencion-blue" if es_hoy else "card-intervencion-red"
            st.markdown(f"""
                <div class="{clase_color}">
                    <b>{row['lugar']}</b><br>{row['motivo']}<br>
                    <small>{row['fecha']}</small>
                </div>
            """, unsafe_allow_html=True)
