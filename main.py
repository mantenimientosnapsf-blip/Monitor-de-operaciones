import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(layout="wide", page_title="SNAP - Monitor de Operaciones")

# Función para obtener datos de tu archivo .db
def get_data(query, params=()):
    try:
        conn = sqlite3.connect('gestion_snap_v5.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error en base de datos: {e}")
        return pd.DataFrame()

# --- ESTILOS CSS (Tu diseño verde y alertas) ---
st.markdown("""
    <style>
    .main { background-color: #0a1a14; }
    .header { background-color: #1db978; color: white; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px; position: relative; }
    .footer-text { font-size: 0.8em; color: #f0f2f6; text-align: right; }
    .card-novedad { background-color: #C0392B; color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #8e0000; }
    .card-alerta-amarilla { background-color: #f1c40f; color: black; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #d4ac0d; }
    .card-plan { border: 2px solid #1db978; background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px; color: #333; }
    .card-plan-alerta { border: 3px solid #f1c40f !important; }
    .intervencion { padding: 10px; border-radius: 6px; margin-bottom: 8px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- VARIABLES DE FECHA ---
hoy_dt = datetime.now()
hoy_str = hoy_dt.strftime("%d/%m/%Y") # Formato para tabla planif
hoy_db = hoy_dt.strftime("%Y-%m-%d") # Formato para tabla eventos

# --- HEADER ---
st.markdown(f"""
    <div class="header">
        <h1>MONITOR DE OPERACIONES</h1>
        <div class="footer-text">Created by Facundo Ramua</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.2, 3, 1.2])

# --- COLUMNA 1: NOVEDADES DEL PERSONAL ---
with col1:
    st.markdown("### ⚠️ NOVEDADES")
    # Consulta a la tabla 'eventos' como en tu script original
    query_nov = "SELECT p, t, hi, hf, fi, ff FROM eventos WHERE fi <= ? AND ff >= ?"
    novedades = get_data(query_nov, (hoy_db, hoy_db))
    
    if not novedades.empty:
        for _, row in novedades.iterrows():
            # Si tiene horario (hi), se pone amarillo según tu regla
            es_horario = row['hi'] and row['hi'].strip() != "" and row['hi'] != "--:--"
            clase = "card-alerta-amarilla" if es_horario else "card-novedad"
            
            st.markdown(f"""
                <div class="{clase}">
                    <b>{row['p']}</b><br>
                    {row['t'].upper()}<br>
                    <small>{row['hi']} a {row['hf']} hs</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Sin novedades hoy.")

# --- COLUMNA 2: PLANIFICACIÓN DEL DÍA ---
with col2:
    st.markdown(f"### PLANIFICACIÓN ({hoy_str})")
    query_plan = """
        SELECT p.id, p.lug, p.resp, p.eq, p.veh, p.hi, p.hf, o.tareas 
        FROM planif p 
        LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.fec = ?
    """
    planificacion = get_data(query_plan, (hoy_str,))
    
    if not planificacion.empty:
        for _, row in planificacion.iterrows():
            # Buscamos si el responsable tiene una alerta horaria hoy
            alerta_y = get_data("SELECT 1 FROM eventos WHERE p=? AND fi<=? AND ff>=? AND hi IS NOT NULL AND hi!='' AND hi!='--:--'", 
                                (row['resp'], hoy_db, hoy_db))
            
            borde_alerta = "card-plan-alerta" if not alerta_y.empty else ""
            
            st.markdown(f"""
                <div class="card-plan {borde_alerta}">
                    <h4 style="color: #1db978; margin:0;">{row['lug'].upper()} ({row['hi']} a {row['hf']})</h4>
                    <b>Responsable:</b> {row['resp']}<br>
                    <b>Personal:</b> {row['eq']}<br>
                    <b>Vehículo:</b> {row['veh']}<br>
                    <hr style="margin:10px 0;">
                    <b style="color: #1db978;">TAREAS:</b><br>
                    {row['tareas'] if row['tareas'] else 'Sin tareas asignadas'}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay servicios programados para hoy.")

# --- COLUMNA 3: ÚLTIMAS INTERVENCIONES ---
with col3:
    st.markdown("### 📅 INTERVENCIONES")
    # Filtramos TALLER para ver sitios reales como en tu dashboard
    query_int = """
        SELECT p.lug, p.fec, o.motivo 
        FROM planif p 
        LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.lug != 'TALLER SANTA FE' 
        ORDER BY p.id DESC LIMIT 15
    """
    interv = get_data(query_int)
    
    if not interv.empty:
        for _, row in interv.iterrows():
            # Color basado en si es de hoy o días atrás
            color = "#3498db" if row['fec'] == hoy_str else "#1db978"
            st.markdown(f"""
                <div class="intervencion" style="background-color: {color};">
                    {row['lug']}<br>
                    <small>{row['fec']} - {row['motivo'] if row['motivo'] else ''}</small>
                </div>
            """, unsafe_allow_html=True)

# Actualización automática cada 15 minutos (900 segundos)
if st.button('Actualizar ahora'):
    st.rerun()
