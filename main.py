import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import extra_streamlit_components as stx

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="SNAP - Monitor de Operaciones")

# --- GESTIÓN DE SESIÓN PERSISTENTE ---
# Eliminamos @st.cache_resource de aquí para evitar el CachedWidgetWarning
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

def check_password():
    if st.session_state.get("password_correct", False):
        return True
    
    # El componente necesita un momento para cargar las cookies
    auth_cookie = cookie_manager.get(cookie="snap_auth_v1")
    
    if auth_cookie == "authorized":
        st.session_state["password_correct"] = True
        return True

    # PANTALLA DE LOGIN
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
        password = st.text_input("Contraseña", type="password")
        mantener = st.checkbox("Mantener sesión iniciada")
        if st.button("Ingresar"):
            if password == "Snap3478":
                st.session_state["password_correct"] = True
                if mantener:
                    cookie_manager.set("snap_auth_v1", "authorized", expires_at=datetime(2027, 1, 1))
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
    except Exception as e:
        return pd.DataFrame()

# --- ESTILOS CSS (Blindaje Total contra iconos y advertencias) ---
st.markdown("""
    <style>
    /* 1. OCULTAR TODO EL TOOLBAR SUPERIOR Y MENÚS */
    [data-testid="stHeader"], header, .stAppHeader, #MainMenu, footer { 
        display: none !important; 
        visibility: hidden !important; 
    }

    /* 2. ELIMINAR EL BOTÓN 'MANAGE APP' Y LA CORONA ROJA */
    .stDeployButton, .stAppDeployButton, .stActionButton, 
    [data-testid="stStatusWidget"], .stStatusWidget, #stDecoration,
    button[title="Manage app"], 
    div[class*="st-emotion-cache-zq5wth"], 
    div[class*="st-emotion-cache-10trblm"],
    div[class*="stAppViewBlockContainer"] > div:last-child,
    .stCustomComponentV1 {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        width: 0px !important;
        opacity: 0 !important;
    }

    /* 3. ESTILOS DE TU INTERFAZ */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    .header { background-color: #1db978; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
    .footer-right { text-align: right; font-size: 0.8em; opacity: 0.8; }
    
    .card-novedad-roja { background-color: #C0392B; color: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #8e0000; }
    .card-novedad-amarilla { background-color: #f1c40f; color: black; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #d4ac0d; }
    
    .card-plan { border: 2px solid #1db978; background-color: white; border-radius: 10px; margin-bottom: 15px; overflow: hidden; color: #333; }
    .card-plan-alerta { border: 3px solid #f1c40f !important; }
    .banner-plan { background-color: #1db978; color: white; padding: 8px 15px; font-weight: bold; }
    .banner-plan-alerta { background-color: #f1c40f; color: black; }
    .body-plan { padding: 12px; }
    
    .intervencion { padding: 10px; border-radius: 6px; margin-bottom: 8px; color: white; font-weight: bold; position: relative; min-height: 85px; display: flex; align-items: center; }
    .dias-atras-box { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); text-align: center; width: 60px; }
    .dias-num { font-size: 1.7em; display: block; line-height: 1; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPO ---
hoy_dt = datetime.now()
hoy_str = hoy_dt.strftime("%d/%m/%Y")
hoy_db = hoy_dt.strftime("%Y-%m-%d")

# --- HEADER ---
st.markdown(f"""
    <div class="header">
        <h1>MONITOR DE OPERACIONES</h1>
        <div class="footer-right">Created by Facundo Ramua</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.5, 1.2])

# --- 1. SECCIÓN NOVEDADES ---
with col1:
    st.markdown("<h3 style='color: #C0392B; text-align: center;'>⚠️ NOVEDADES</h3>", unsafe_allow_html=True)
    nov_df = get_data("SELECT p, t, hi, hf, fi, ff FROM eventos WHERE fi <= ? AND ff >= ?", (hoy_db, hoy_db))
    if not nov_df.empty:
        for _, row in nov_df.iterrows():
            es_horario = row['hi'] and row['hi'].strip() not in ["", "--:--"]
            clase = "card-novedad-amarilla" if es_horario else "card-novedad-roja"
            info = f"{row['hi']} a {row['hf']} hs" if es_horario else "Jornada Completa"
            st.markdown(f'<div class="{clase}"><b>{row["p"]}</b><br>{row["t"].upper()}<br><small>{info}</small></div>', unsafe_allow_html=True)

# --- 2. SECCIÓN PLANIFICACIÓN ---
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
            
            st.markdown(f"""
                <div class="card-plan {'card-plan-alerta' if es_alerta else ''}">
                    <div class="banner-plan {'banner-plan-alerta' if es_alerta else ''}">{row['lug'].upper()} - {row['hi']} a {row['hf']}</div>
                    <div class="body-plan">
                        <b>RESPONSABLE:</b> {row['resp']}<br>
                        <b>PERSONAL:</b> {row['eq']}<br>
                        <b>VEHÍCULO:</b> {row['veh']}<br>
                        <p style="margin-top:10px; color:#1db978; font-weight:bold; margin-bottom:4px;">TAREAS:</p>
                        {row['tareas'].replace('[X]', '🟦').replace('[ ]', '⬜') if row['tareas'] else 'Sin tareas asignadas'}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 3. SECCIÓN INTERVENCIONES ---
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
            tag = "HOY" if diff == 0 else f"{diff} DÍAS"
            st.markdown(f"""
                <div class="intervencion" style="background-color: {color}; color: {txt_c};">
                    <div style="width: 75%; line-height: 1.1;">
                        <span style="font-size:1em;">{row['lug'].upper()}</span><br>
                        <small style="opacity:0.7;">{row['fec']}</small>
                    </div>
                    <div class="dias-atras-box"><span class="dias-num">{tag}</span></div>
                </div>
            """, unsafe_allow_html=True)
