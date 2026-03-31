import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="SNAP - Monitor de Operaciones")

def check_password():
    """Verifica contraseña usando parámetros de URL para persistencia total."""
    # 1. Revisar si ya está en la sesión actual
    if st.session_state.get("password_correct", False):
        return True

    # 2. Revisar si el parámetro de autorización está en la URL
    query_params = st.query_params
    if query_params.get("auth") == "authorized":
        st.session_state["password_correct"] = True
        return True

    # 3. PANTALLA DE LOGIN
    st.markdown("""
        <style>
        [data-testid="stHeader"], .stAppHeader { display: none !important; }
        .login-box {
            background-color: #1db978; padding: 30px; border-radius: 10px;
            color: white; text-align: center; max-width: 400px; margin: 100px auto 20px auto;
        }
        </style>
        <div class="login-box">
            <h2>🔐 ACCESO SNAP</h2>
            <p>Ingresá la contraseña para continuar</p>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        password = st.text_input("Contraseña", type="password", key="pwd_input")
        
        if st.button("Ingresar"):
            if password == "Snap3478":
                st.session_state["password_correct"] = True
                st.query_params["auth"] = "authorized"
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

if not check_password():
    st.stop()

# --- FUNCIONES DE DATOS ---
def get_data(query, params=()):
    try:
        conn = sqlite3.connect('gestion_snap_v5.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    [data-testid="stHeader"], header, .stAppHeader, #MainMenu, footer,
    .stDeployButton, .stAppDeployButton, .stActionButton, 
    [data-testid="stStatusWidget"], .stStatusWidget, #stDecoration,
    button[title="Manage app"], 
    div[class*="st-emotion-cache-zq5wth"], 
    div[class*="st-emotion-cache-10trblm"],
    div[class*="stAppViewBlockContainer"] > div:last-child {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        opacity: 0 !important;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    .header { background-color: #1db978; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
    .footer-right { text-align: right; font-size: 0.8em; opacity: 0.8; }
    .card-novedad-roja { background-color: #C0392B; color: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #8e0000; }
    .card-novedad-amarilla { background-color: #f1c40f; color: black; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #d4ac0d; }
    .card-plan { border: 2px solid #1db978; background-color: white; border-radius: 10px; margin-bottom: 15px; overflow: hidden; color: #333; }
    .card-plan-alerta { border: 3px solid #f1c40f !important; }
    .banner-plan { background-color: #1db978; color: white; padding: 8px 15px; font-weight: bold; }
    .banner-plan-alerta { background-color: #f1c40f; color: black; }
    .body-plan { padding: 15px; }
    .task-row { font-size: 1.05em; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; }
    .task-icon { font-size: 1.3em; line-height: 1; }
    .intervencion { padding: 10px; border-radius: 6px; margin-bottom: 8px; color: white; font-weight: bold; position: relative; min-height: 85px; display: flex; align-items: center; }
    .dias-atras-box { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); text-align: center; width: 65px; }
    .dias-num { font-size: 1.8em; display: block; line-height: 1; }
    .dias-txt { font-size: 0.65em; display: block; line-height: 1.1; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

hoy_dt = datetime.now()
hoy_str = hoy_dt.strftime("%d/%m/%Y")
hoy_db = hoy_dt.strftime("%Y-%m-%d")

st.markdown(f'<div class="header"><h1>MONITOR DE OPERACIONES</h1><div class="footer-right">Created by Facundo Ramua</div></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.5, 1.2])

# --- 1. NOVEDADES ---
with col1:
    st.markdown("<h3 style='color: #C0392B; text-align: center;'>⚠️<br>NOVEDADES DEL PERSONAL</h3>", unsafe_allow_html=True)
    nov_df = get_data("SELECT p, t, hi, hf, fi, ff FROM eventos WHERE fi <= ? AND ff >= ?", (hoy_db, hoy_db))
    if not nov_df.empty:
        for _, row in nov_df.iterrows():
            es_horario = row['hi'] and row['hi'].strip() not in ["", "--:--"]
            clase = "card-novedad-amarilla" if es_horario else "card-novedad-roja"
            info = f"{row['hi']} a {row['hf']} hs" if es_horario else "Jornada Completa"
            st.markdown(f'<div class="{clase}"><b>{row["p"]}</b><br>{row["t"].upper()}<br><small>{info}</small></div>', unsafe_allow_html=True)

# --- 2. PLANIFICACIÓN ---
with col2:
    st.markdown(f"<h3 style='text-align: center;'>PLANIFICACIÓN <br> ({hoy_str})</h3>", unsafe_allow_html=True)
    plan_df = get_data("""
        SELECT p.id, p.lug, p.resp, p.eq, p.veh, p.hi, p.hf, o.tareas 
        FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.fec = ? ORDER BY p.lug ASC""", (hoy_str,))
    
    if not plan_df.empty:
        for _, row in plan_df.iterrows():
            alerta = get_data("SELECT 1 FROM eventos WHERE p=? AND fi<=? AND ff>=? AND hi IS NOT NULL AND hi!='' AND hi!='--:--'", (row['resp'], hoy_db, hoy_db))
            es_alerta = not alerta.empty
            
            tareas_html = ""
            if row['tareas']:
                for linea in row['tareas'].split('\n'):
                    if not linea.strip(): continue
                    icono = "🟦" if "[X]" in linea.upper() else "⬜"
                    texto = linea.replace("[X]", "").replace("[ ]", "").replace("[", "").replace("]", "").strip()
                    tareas_html += f'<div class="task-row"><span class="task-icon">{icono}</span><span>{texto}</span></div>'
            else:
                tareas_html = "Sin tareas asignadas"

            st.markdown(f"""
                <div class="card-plan {'card-plan-alerta' if es_alerta else ''}">
                    <div class="banner-plan {'banner-plan-alerta' if es_alerta else ''}">{row['lug'].upper()} - {row['hi']} a {row['hf']}</div>
                    <div class="body-plan">
                        <b>RESPONSABLE:</b> {row['resp']}<br>
                        <b>PERSONAL:</b> {row['eq']}<br>
                        <b>VEHÍCULO:</b> {row['veh']}<br>
                        <p style="margin-top:10px; color:#1db978; font-weight:bold; margin-bottom:8px;">TAREAS A REALIZAR:</p>
                        {tareas_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 3. INTERVENCIONES ---
with col3:
    st.markdown("<h3 style='text-align: center;'>📅 <br> ÚLTIMAS INTERVENCIONES</h3>", unsafe_allow_html=True)
    int_df = get_data("SELECT p.lug, p.fec, o.motivo FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl WHERE p.lug != 'TALLER SANTA FE'")
    if not int_df.empty:
        int_df['f_dt'] = pd.to_datetime(int_df['fec'], format='%d/%m/%Y', errors='coerce')
        int_df = int_df[int_df['f_dt'] <= hoy_dt].sort_values('f_dt', ascending=True).drop_duplicates('lug', keep='last')
        for _, row in int_df.iterrows():
            diff = (hoy_dt - row['f_dt']).days
            color = "#3498db" if diff == 0 else ("#1db978" if diff < 8 else ("#f1c40f" if diff < 15 else "#C0392B"))
            txt_c = "black" if color == "#f1c40f" else "white"
            tag = '<span class="dias-num" style="font-size:1.2em;">HOY</span>' if diff == 0 else f'<span class="dias-num">{diff}</span><span class="dias-txt">{"DÍA" if diff==1 else "DÍAS"}<br>ATRÁS</span>'
            st.markdown(f"""
                <div class="intervencion" style="background-color: {color}; color: {txt_c};">
                    <div style="width: 75%; line-height: 1.2;">
                        <span style="font-size:1.1em;">{row['lug'].upper()}</span><br>
                        <small style="font-weight: normal; opacity: 0.9;">{row['motivo'] if row['motivo'] else 'S/M'}</small><br>
                        <small style="opacity:0.7; font-weight: normal;">{row['fec']}</small>
                    </div>
                    <div class="dias-atras-box">{tag}</div>
                </div>
            """, unsafe_allow_html=True)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    [data-testid="stHeader"], header, .stAppHeader, #MainMenu, footer,
    .stDeployButton, .stAppDeployButton, .stActionButton, 
    [data-testid="stStatusWidget"], .stStatusWidget, #stDecoration,
    button[title="Manage app"], 
    div[class*="st-emotion-cache-zq5wth"], 
    div[class*="st-emotion-cache-10trblm"],
    div[class*="stAppViewBlockContainer"] > div:last-child {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        opacity: 0 !important;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    .header { background-color: #1db978; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
    .footer-right { text-align: right; font-size: 0.8em; opacity: 0.8; }
    .card-novedad-roja { background-color: #C0392B; color: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #8e0000; }
    .card-novedad-amarilla { background-color: #f1c40f; color: black; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #d4ac0d; }
    .card-plan { border: 2px solid #1db978; background-color: white; border-radius: 10px; margin-bottom: 15px; overflow: hidden; color: #333; }
    .card-plan-alerta { border: 3px solid #f1c40f !important; }
    .banner-plan { background-color: #1db978; color: white; padding: 8px 15px; font-weight: bold; }
    .banner-plan-alerta { background-color: #f1c40f; color: black; }
    .body-plan { padding: 15px; }
    .task-row { font-size: 1.05em; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; }
    .task-icon { font-size: 1.3em; line-height: 1; }
    .intervencion { padding: 10px; border-radius: 6px; margin-bottom: 8px; color: white; font-weight: bold; position: relative; min-height: 85px; display: flex; align-items: center; }
    .dias-atras-box { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); text-align: center; width: 65px; }
    .dias-num { font-size: 1.8em; display: block; line-height: 1; }
    .dias-txt { font-size: 0.65em; display: block; line-height: 1.1; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

hoy_dt = datetime.now()
hoy_str = hoy_dt.strftime("%d/%m/%Y")
hoy_db = hoy_dt.strftime("%Y-%m-%d")

st.markdown(f'<div class="header"><h1>MONITOR DE OPERACIONES</h1><div class="footer-right">Created by Facundo Ramua</div></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.5, 1.2])

# --- 1. NOVEDADES ---
with col1:
    st.markdown("<h3 style='color: #C0392B; text-align: center;'>⚠️ NOVEDADES</h3>", unsafe_allow_html=True)
    nov_df = get_data("SELECT p, t, hi, hf, fi, ff FROM eventos WHERE fi <= ? AND ff >= ?", (hoy_db, hoy_db))
    if not nov_df.empty:
        for _, row in nov_df.iterrows():
            es_horario = row['hi'] and row['hi'].strip() not in ["", "--:--"]
            # Corrección de sintaxis eliminando etiquetas residuales
            clase = "card-novedad-amarilla" if es_horario else "card-novedad-roja"
            info = f"{row['hi']} a {row['hf']} hs" if es_horario else "Jornada Completa"
            st.markdown(f'<div class="{clase}"><b>{row["p"]}</b><br>{row["t"].upper()}<br><small>{info}</small></div>', unsafe_allow_html=True)

# --- 2. PLANIFICACIÓN (Info Completa) ---
with col2:
    st.markdown(f"<h3 style='text-align: center;'>PLANIFICACIÓN ({hoy_str})</h3>", unsafe_allow_html=True)
    plan_df = get_data("""
        SELECT p.id, p.lug, p.resp, p.eq, p.veh, p.hi, p.hf, o.tareas 
        FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.fec = ? ORDER BY p.lug ASC""", (hoy_str,))
    
    if not plan_df.empty:
        for _, row in plan_df.iterrows():
            alerta = get_data("SELECT 1 FROM eventos WHERE p=? AND fi<=? AND ff>=? AND hi IS NOT NULL AND hi!='' AND hi!='--:--'", (row['resp'], hoy_db, hoy_db))
            es_alerta = not alerta.empty
            
            tareas_html = ""
            if row['tareas']:
                for linea in row['tareas'].split('\n'):
                    if not linea.strip(): continue
                    icono = "🟦" if "[X]" in linea.upper() else "⬜"
                    texto = linea.replace("[X]", "").replace("[ ]", "").replace("[", "").replace("]", "").strip()
                    tareas_html += f'<div class="task-row"><span class="task-icon">{icono}</span><span>{texto}</span></div>'
            else:
                tareas_html = "Sin tareas asignadas"

            st.markdown(f"""
                <div class="card-plan {'card-plan-alerta' if es_alerta else ''}">
                    <div class="banner-plan {'banner-plan-alerta' if es_alerta else ''}">{row['lug'].upper()} - {row['hi']} a {row['hf']}</div>
                    <div class="body-plan">
                        <b>RESPONSABLE:</b> {row['resp']}<br>
                        <b>PERSONAL:</b> {row['eq']}<br>
                        <b>VEHÍCULO:</b> {row['veh']}<br>
                        <p style="margin-top:10px; color:#1db978; font-weight:bold; margin-bottom:8px;">TAREAS A REALIZAR:</p>
                        {tareas_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 3. INTERVENCIONES ---
with col3:
    st.markdown("<h3 style='text-align: center;'>📅 ÚLTIMAS</h3>", unsafe_allow_html=True)
    int_df = get_data("SELECT p.lug, p.fec, o.motivo FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl WHERE p.lug != 'TALLER SANTA FE'")
    if not int_df.empty:
        int_df['f_dt'] = pd.to_datetime(int_df['fec'], format='%d/%m/%Y', errors='coerce')
        int_df = int_df[int_df['f_dt'] <= hoy_dt].sort_values('f_dt', ascending=True).drop_duplicates('lug', keep='last')
        for _, row in int_df.iterrows():
            diff = (hoy_dt - row['f_dt']).days
            color = "#3498db" if diff == 0 else ("#1db978" if diff < 8 else ("#f1c40f" if diff < 15 else "#C0392B"))
            txt_c = "black" if color == "#f1c40f" else "white"
            tag = '<span class="dias-num" style="font-size:1.2em;">HOY</span>' if diff == 0 else f'<span class="dias-num">{diff}</span><span class="dias-txt">{"DÍA" if diff==1 else "DÍAS"}<br>ATRÁS</span>'
            st.markdown(f"""
                <div class="intervencion" style="background-color: {color}; color: {txt_c};">
                    <div style="width: 75%; line-height: 1.2;">
                        <span style="font-size:1.1em;">{row['lug'].upper()}</span><br>
                        <small style="font-weight: normal; opacity: 0.9;">{row['motivo'] if row['motivo'] else 'S/M'}</small><br>
                        <small style="opacity:0.7; font-weight: normal;">{row['fec']}</small>
                    </div>
                    <div class="dias-atras-box">{tag}</div>
                </div>
            """, unsafe_allow_html=True)
