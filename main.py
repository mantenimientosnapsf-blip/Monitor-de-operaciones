import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="SNAP - Monitor de Operaciones")

# --- FUNCIONES DE DATOS ---
def get_data(query, params=()):
    try:
        conn = sqlite3.connect('gestion_snap_v5.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- ESTILOS CSS (Réplica de tu Dashboard de escritorio) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .header { background-color: #1db978; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px; }
    .card-novedad-roja { background-color: #C0392B; color: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #8e0000; }
    .card-novedad-amarilla { background-color: #f1c40f; color: black; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #d4ac0d; }
    .card-plan { border: 2px solid #1db978; background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px; color: #333; }
    .card-plan-alerta { border: 3px solid #f1c40f !important; }
    .banner-plan { background-color: #1db978; color: white; padding: 5px 15px; border-radius: 5px 5px 0 0; margin: -15px -15px 10px -15px; font-weight: bold; }
    .banner-plan-alerta { background-color: #f1c40f; color: black; }
    .intervencion { padding: 10px; border-radius: 6px; margin-bottom: 8px; color: white; font-weight: bold; position: relative; }
    .dias-atras { float: right; font-size: 1.2em; opacity: 0.8; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE FECHAS ---
hoy_dt = datetime.now()
hoy_str = hoy_dt.strftime("%d/%m/%Y")
hoy_db = hoy_dt.strftime("%Y-%m-%d")

# --- HEADER ---
st.markdown(f'<div class="header"><h1>MONITOR DE OPERACIONES</h1><p>Created by Facundo Ramua</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.5, 1.2])

# --- 1. NOVEDADES DEL PERSONAL ---
with col1:
    st.markdown("<h3 style='color: #C0392B; text-align: center;'>⚠️ NOVEDADES</h3>", unsafe_allow_html=True)
    nov_df = get_data("SELECT p, t, hi, hf, fi, ff FROM eventos WHERE fi <= ? AND ff >= ?", (hoy_db, hoy_db))
    
    if not nov_df.empty:
        for _, row in nov_df.iterrows():
            es_horario = row['hi'] and row['hi'].strip() not in ["", "--:--"]
            clase = "card-novedad-amarilla" if es_horario else "card-novedad-roja"
            
            # Formateo de fecha para mostrar
            f_inicio = datetime.strptime(row['fi'], "%Y-%m-%d").strftime("%d/%m/%Y")
            f_fin = datetime.strptime(row['ff'], "%Y-%m-%d").strftime("%d/%m/%Y")
            info_tiempo = f"{f_inicio} | {row['hi']} a {row['hf']} hs" if es_horario else f"Del {f_inicio} al {f_fin}"
            
            st.markdown(f"""
                <div class="{clase}">
                    <b style="font-size: 1.1em;">{row['p']}</b><br>
                    {row['t'].upper()}<br>
                    <small>{info_tiempo}</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Sin novedades.")

# --- 2. PLANIFICACIÓN DEL DÍA ---
with col2:
    st.markdown(f"<h3 style='text-align: center;'>PLANIFICACIÓN ({hoy_str})</h3>", unsafe_allow_html=True)
    plan_df = get_data("""
        SELECT p.id, p.lug, p.resp, p.eq, p.veh, p.hi, p.hf, o.tareas 
        FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.fec = ? ORDER BY p.hi ASC""", (hoy_str,))
    
    if not plan_df.empty:
        for _, row in plan_df.iterrows():
            # Check de alerta amarilla para el responsable
            alerta = get_data("SELECT 1 FROM eventos WHERE p=? AND fi<=? AND ff>=? AND hi IS NOT NULL AND hi!='' AND hi!='--:--'", 
                              (row['resp'], hoy_db, hoy_db))
            
            es_alerta = not alerta.empty
            clase_card = "card-plan-alerta" if es_alerta else ""
            clase_banner = "banner-plan-alerta" if es_alerta else ""
            
            st.markdown(f"""
                <div class="card-plan {clase_card}">
                    <div class="banner-plan {clase_banner}">
                        {row['lug'].upper()} - {row['hi']} a {row['hf']}
                    </div>
                    <b>RESPONSABLE:</b> {row['resp']}<br>
                    <b>PERSONAL:</b> {row['eq']}<br>
                    <b>VEHÍCULO:</b> {row['veh']}<br>
                    <p style="margin-top:10px; color:#1db978; font-weight:bold;">TAREAS A REALIZAR:</p>
                    <small>{row['tareas'].replace('\\n', '<br>') if row['tareas'] else 'Sin tareas'}</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay planificación para hoy.")

# --- 3. ÚLTIMAS INTERVENCIONES ---
with col3:
    st.markdown("<h3 style='text-align: center;'>📅 INTERVENCIONES</h3>", unsafe_allow_html=True)
    int_df = get_data("SELECT p.lug, p.fec, o.motivo FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl WHERE p.lug != 'TALLER SANTA FE'")
    
    if not int_df.empty:
        # Lógica de "Días atrás"
        int_df['f_dt'] = pd.to_datetime(int_df['fec'], format='%d/%m/%Y', errors='coerce')
        int_df = int_df.dropna(subset=['f_dt']).sort_values('f_dt', ascending=False).drop_duplicates('lug').head(12)
        
        for _, row in int_df.iterrows():
            diff = (hoy_dt - row['f_dt']).days
            # Colores según tu dashboard
            color = "#3498db" if diff == 0 else ("#1db978" if diff < 8 else ("#f1c40f" if diff < 15 else "#C0392B"))
            txt_color = "black" if color == "#f1c40f" else "white"
            tag_hoy = "HOY" if diff == 0 else f"{diff}"
            
            st.markdown(f"""
                <div class="intervencion" style="background-color: {color}; color: {txt_color};">
                    <span class="dias-atras">{tag_hoy}</span>
                    {row['lug'].upper()}<br>
                    <small>{row['motivo'] if row['motivo'] else 'S/M'}</small><br>
                    <small style="opacity:0.8;">{row['fec']}</small>
                </div>
            """, unsafe_allow_html=True)

# Auto-refresh
if st.button('🔄 Actualizar'):
    st.rerun()
