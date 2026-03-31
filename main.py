import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="SNAP - Monitor de Operaciones")

# --- CONTROL DE ACCESO ---
def check_password():
    """Retorna True si el usuario ingresó la contraseña correcta."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Pantalla de Login
    st.markdown("""
        <style>
        [data-testid="stHeader"] { display: none !important; }
        .login-box {
            background-color: #1db978;
            padding: 30px;
            border-radius: 10px;
            color: white;
            text-align: center;
            max-width: 400px;
            margin: 100px auto;
        }
        </style>
        <div class="login-box">
            <h2>🔐 ACCESO SNAP</h2>
            <p>Ingresá la contraseña para continuar</p>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        password = st.text_input("Contraseña", type="password", placeholder="Escribí aquí...")
        if st.button("Ingresar"):
            if password == "Snap3478":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

# --- SI NO ESTÁ LOGUEADO, CORTE AQUÍ ---
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
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- ESTILOS CSS DEL MONITOR ---
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .block-container { padding-top: 2rem !important; }

    .main { background-color: #f0f2f6; }
    .header { background-color: #1db978; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    .header h1 { margin-bottom: 5px; text-align: center; }
    .footer-left { text-align: left; font-size: 0.9em; opacity: 0.9; padding-left: 10px; }
    
    .card-novedad-roja { background-color: #C0392B; color: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #8e0000; }
    .card-novedad-amarilla { background-color: #f1c40f; color: black; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 10px solid #d4ac0d; }
    
    .card-plan { border: 2px solid #1db978; background-color: white; padding: 0px; border-radius: 10px; margin-bottom: 15px; color: #333; overflow: hidden; }
    .banner-plan { background-color: #1db978; color: white; padding: 8px 15px; font-weight: bold; font-size: 1.1em; }
    .body-plan { padding: 15px; }
    
    .task-row { font-size: 1.05em; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; }
    .intervencion { padding: 10px; border-radius: 6px; margin-bottom: 8px; color: white; font-weight: bold; position: relative; min-height: 85px; display: flex; align-items: center; }
    .dias-atras-box { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); text-align: center; width: 65px; }
    .dias-num { font-size: 1.8em; display: block; line-height: 1; }
    .dias-txt { font-size: 0.65em; display: block; line-height: 1.1; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE FECHAS ---
hoy_dt = datetime.now()
hoy_str = hoy_dt.strftime("%d/%m/%Y")
hoy_db = hoy_dt.strftime("%Y-%m-%d")

# --- HEADER ---
st.markdown(f"""
    <div class="header">
        <h1>MONITOR DE OPERACIONES</h1>
        <div class="footer-left">Created by Facundo Ramua</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.5, 1.2])

# --- 1. NOVEDADES ---
with col1:
    st.markdown("<h3 style='color: #C0392B; text-align: center;'>⚠️ NOVEDADES</h3>", unsafe_allow_html=True)
    nov_df = get_data("SELECT p, t, hi, hf, fi, ff FROM eventos WHERE fi <= ? AND ff >= ?", (hoy_db, hoy_db))
    if not nov_df.empty:
        for _, row in nov_df.iterrows():
            es_horario = row['hi'] and row['hi'].strip() not in ["", "--:--"]
            clase = "card-novedad-amarilla" if es_horario else "card-novedad-roja"
            f_ini = datetime.strptime(row['fi'], "%Y-%m-%d").strftime("%d/%m/%Y")
            info = f"{f_ini} | {row['hi']} a {row['hf']} hs" if es_horario else f"Hasta {datetime.strptime(row['ff'], '%Y-%m-%d').strftime('%d/%m/%Y')}"
            st.markdown(f'<div class="{clase}"><b>{row["p"]}</b><br>{row["t"].upper()}<br><small>{info}</small></div>', unsafe_allow_html=True)

# --- 2. PLANIFICACIÓN ---
with col2:
    st.markdown(f"<h3 style='text-align: center;'>PLANIFICACIÓN ({hoy_str})</h3>", unsafe_allow_html=True)
    plan_df = get_data("""
        SELECT p.id, p.lug, p.resp, p.eq, p.veh, p.hi, p.hf, o.tareas 
        FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.fec = ? ORDER BY p.lug ASC""", (hoy_str,))
    
    if not plan_df.empty:
        for _, row in plan_df.iterrows():
            st.markdown(f"""
                <div class="card-plan">
                    <div class="banner-plan">{row['lug'].upper()} - {row['hi']} a {row['hf']}</div>
                    <div class="body-plan">
                        <b>RESPONSABLE:</b> {row['resp']}<br>
                        <b>PERSONAL:</b> {row['eq']}<br>
                        <b>VEHÍCULO:</b> {row['veh']}<br>
                        <p style="margin-top:10px; color:#1db978; font-weight:bold;">TAREAS:</p>
                        {row['tareas'] if row['tareas'] else 'Sin tareas'}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 3. INTERVENCIONES ---
with col3:
    st.markdown("<h3 style='text-align: center;'>📅 INTERVENCIONES</h3>", unsafe_allow_html=True)
    int_df = get_data("SELECT p.lug, p.fec, o.motivo FROM planif p LEFT JOIN ordenes o ON p.id = o.id_pl WHERE p.lug != 'TALLER SANTA FE'")
    if not int_df.empty:
        int_df['f_dt'] = pd.to_datetime(int_df['fec'], format='%d/%m/%Y', errors='coerce')
        int_df = int_df[int_df['f_dt'] <= hoy_dt].sort_values('f_dt', ascending=True).drop_duplicates('lug', keep='last')
        
        for _, row in int_df.iterrows():
            diff = (hoy_dt - row['f_dt']).days
            color = "#3498db" if diff == 0 else ("#1db978" if diff < 8 else ("#f1c40f" if diff < 15 else "#C0392B"))
            st.markdown(f"""
                <div class="intervencion" style="background-color: {color};">
                    <div style="width: 70%;">{row['lug'].upper()}<br><small>{row['fec']}</small></div>
                    <div class="dias-atras-box"><span class="dias-num">{diff if diff > 0 else 'HOY'}</span></div>
                </div>
            """, unsafe_allow_html=True)
