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

# --- ESTILOS CSS (Ajustados para réplica exacta) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .header { background-color: #1db978; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px; }
    .card-novedad-roja { background-color: #C0392B; color: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #8e0000; font-family: Arial; }
    .card-novedad-amarilla { background-color: #f1c40f; color: black; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #d4ac0d; font-family: Arial; }
    .card-plan { border: 2px solid #1db978; background-color: white; padding: 0px; border-radius: 10px; margin-bottom: 15px; color: #333; overflow: hidden; }
    .card-plan-alerta { border: 3px solid #f1c40f !important; }
    .banner-plan { background-color: #1db978; color: white; padding: 8px 15px; font-weight: bold; font-size: 1.1em; }
    .banner-plan-alerta { background-color: #f1c40f; color: black; }
    .body-plan { padding: 15px; }
    .intervencion { padding: 10px; border-radius: 6px; margin-bottom: 8px; color: white; font-weight: bold; position: relative; font-family: Arial; }
    .dias-atras-box { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); text-align: center; line-height: 1; }
    .dias-num { font-size: 1.6em; display: block; }
    .dias-txt { font-size: 0.6em; display: block; }
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
            f_inicio = datetime.strptime(row['fi'], "%Y-%m-%d").strftime("%d/%m/%Y")
            f_fin = datetime.strptime(row['ff'], "%Y-%m-%d").strftime("%d/%m/%Y")
            info_tiempo = f"{f_inicio} | {row['hi']} a {row['hf']} hs" if es_horario else f"Del {f_inicio} al {f_fin}"
            
            st.markdown(f'<div class="{clase}"><b>{row["p"]}</b><br>{row["t"].upper()}<br><small>{info_tiempo}</small></div>', unsafe_allow_html=True)

# --- 2. PLANIFICACIÓN DEL DÍA ---
with col2:
    st.markdown(f"<h3 style='text-align: center;'>PLANIFICACIÓN ({hoy_str})</h3>", unsafe_allow_html=True)
    plan_df = get_data("""
        SELECT p.id, p.lug, p.resp, p.eq, p.veh, p.hi, p.hf, o.tareas 
        FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.fec = ? ORDER BY p.lug ASC, p.hi ASC""", (hoy_str,))
    
    if not plan_df.empty:
        for _, row in plan_df.iterrows():
            alerta = get_data("SELECT 1 FROM eventos WHERE p=? AND fi<=? AND ff>=? AND hi IS NOT NULL AND hi!='' AND hi!='--:--'", (row['resp'], hoy_db, hoy_db))
            es_alerta = not alerta.empty
            clase_card = "card-plan-alerta" if es_alerta else ""
            clase_banner = "banner-plan-alerta" if es_alerta else ""
            
            # Formateo de tareas: Corchetes por Cuadrados
            tareas_html = ""
            if row['tareas']:
                for linea in row['tareas'].split('\n'):
                    if not linea.strip(): continue
                    # Reemplazamos [X] por cuadrado lleno y [ ] por vacío
                    linea_fmt = linea.replace("[X]", "■").replace("[ ]", "□").replace("[", "□").replace("]", "")
                    tareas_html += f"• {linea_fmt}<br>"
            else:
                tareas_html = "Sin tareas asignadas"

            st.markdown(f"""
                <div class="card-plan {clase_card}">
                    <div class="banner-plan {clase_banner}">{row['lug'].upper()} - {row['hi']} a {row['hf']}</div>
                    <div class="body-plan">
                        <b>RESPONSABLE:</b> {row['resp']}<br>
                        <b>PERSONAL:</b> {row['eq']}<br>
                        <b>VEHÍCULO:</b> {row['veh']}<br>
                        <p style="margin-top:10px; color:#1db978; font-weight:bold; margin-bottom:5px;">TAREAS A REALIZAR:</p>
                        <div style="font-size: 0.95em; line-height: 1.4;">{tareas_html}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 3. ÚLTIMAS INTERVENCIONES ---
with col3:
    st.markdown("<h3 style='text-align: center;'>📅 INTERVENCIONES</h3>", unsafe_allow_html=True)
    int_df = get_data("SELECT p.lug, p.fec, o.motivo FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl WHERE p.lug != 'TALLER SANTA FE'")
    
    if not int_df.empty:
        int_df['f_dt'] = pd.to_datetime(int_df['fec'], format='%d/%m/%Y', errors='coerce')
        # Filtramos para no mostrar fechas futuras y ordenamos: más recientes arriba
        int_df = int_df[int_df['f_dt'] <= hoy_dt].sort_values('f_dt', ascending=False)
        int_df = int_df.drop_duplicates('lug').head(15)
        
        for _, row in int_df.iterrows():
            diff = (hoy_dt - row['f_dt']).days
            color = "#3498db" if diff == 0 else ("#1db978" if diff < 8 else ("#f1c40f" if diff < 15 else "#C0392B"))
            txt_c = "black" if color == "#f1c40f" else "white"
            
            # Caja de "Días atrás" idéntica a la app
            if diff == 0:
                tag_dias = '<span class="dias-num" style="font-size:1.1em; margin-top:8px;">HOY</span>'
            else:
                label_atras = "DÍA<br>ATRÁS" if diff == 1 else "DÍAS<br>ATRÁS"
                tag_dias = f'<span class="dias-num">{diff}</span><span class="dias-txt">{label_atras}</span>'
            
            st.markdown(f"""
                <div class="intervencion" style="background-color: {color}; color: {txt_c};">
                    <div class="dias-atras-box">{tag_dias}</div>
                    <div style="width: 80%;">{row['lug'].upper()}<br>
                    <small style="font-weight: normal;">{row['motivo'] if row['motivo'] else 'S/M'}</small><br>
                    <small style="opacity:0.8; font-weight: normal;">{row['fec']}</small></div>
                </div>
            """, unsafe_allow_html=True)
