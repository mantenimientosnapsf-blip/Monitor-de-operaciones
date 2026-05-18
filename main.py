import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import datetime as dt_mod
import time
import os
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    layout="wide", 
    page_title="SNAP - Monitor de Operaciones",
    page_icon="🟢"
)

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos la ruta local si existe, de lo contrario busca la relativa en la nube de GitHub
DB_PATH = r"C:\Users\Usuario\Documents\APP\Planificación diaria\gestion_snap_v5.db"
if not os.path.exists(DB_PATH):
    DB_PATH = "gestion_snap_v5.db"

# --- CONTROL DE ACCESO ---
def check_password():
    """Verifica contraseña usando parámetros de URL para persistencia total."""
    if st.session_state.get("password_correct", False):
        return True

    query_params = st.query_params
    if query_params.get("auth") == "authorized":
        st.session_state["password_correct"] = True
        return True

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

# Auto-refresh cada 1 hora
st_autorefresh(interval=3600000, key="datarefresh")

# Inicializar el estado de la página actual si no existe
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "monitor"

# --- FUNCIONES DE DATOS ---
def get_data(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# --- ESTILOS CSS GENERALES ---
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
    .header-container { background-color: #1db978; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; position: relative; text-align: center;}
    .footer-right { text-align: right; font-size: 0.8em; opacity: 0.8; margin-top: 5px;}
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
    
    /* Ajustes estéticos para los botones de navegación */
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)


# ==========================================
# VISTA 1: MONITOR DE OPERACIONES
# ==========================================
if st.session_state["current_page"] == "monitor":
    
    # Header adaptado con columnas para contener el botón de navegación a la derecha
    st.markdown('<div class="header-container"><h1>MONITOR DE OPERACIONES</h1><div class="footer-right">Created by Facundo Ramua</div></div>', unsafe_allow_html=True)
    
    # Barra de navegación superior derecha
    nav_col1, nav_col2 = st.columns([4, 1])
    with nav_col2:
        if st.button("Ver Flujo de Tareas ➡️"):
            st.session_state["current_page"] = "flujo"
            st.rerun()

    hoy_dt = datetime.now()
    hoy_str = hoy_dt.strftime("%d/%m/%Y")
    hoy_db = hoy_dt.strftime("%Y-%m-%d")

    col1, col2, col3 = st.columns([1, 2.5, 1.2])

    # --- 1. NOVEDADES ---
    with col1:
        st.markdown("<h4 style='color: #C0392B; text-align: center;'>⚠️ NOVEDADES DEL PERSONAL</h4>", unsafe_allow_html=True)
        nov_df = get_data("SELECT p, t, hi, hf, fi, ff FROM eventos WHERE fi <= ? AND ff >= ?", (hoy_db, hoy_db))
        
        if not nov_df.empty:
            for _, row in nov_df.iterrows():
                f_inicio = datetime.strptime(row['fi'], "%Y-%m-%d").strftime("%d/%m")
                f_fin = datetime.strptime(row['ff'], "%Y-%m-%d").strftime("%d/%m")
                rango_fecha = f"{f_inicio} al {f_fin}" if f_inicio != f_fin else f_inicio

                es_horario = row['hi'] and row['hi'].strip() not in ["", "--:--"]
                clase = "card-novedad-amarilla" if es_horario else "card-novedad-roja"
                
                if es_horario:
                    info_texto = f"{rango_fecha} | {row['hi']} a {row['hf']} hs"
                else:
                    info_texto = f"Fecha: {rango_fecha}"

                st.markdown(f"""
                    <div class="{clase}">
                        <b>{row['p']}</b><br>
                        {row['t'].upper()}<br>
                        <small>{info_texto}</small>
                    </div>
                """, unsafe_allow_html=True)

    # --- 2. PLANIFICACIÓN ---
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
                        icono = "✔️" if "[X]" in linea.upper() else "⬜"
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
        st.markdown("<h4 style='text-align: center;'>📅 ÚLTIMAS INTERVENCIONES</h3>", unsafe_allow_html=True)
        int_df = get_data("""
        SELECT p.lug, p.fec, o.motivo 
        FROM planif p 
        LEFT JOIN ordenes o ON p.id = o.id_pl 
        WHERE p.lug != 'TALLER SANTA FE' 
          AND p.lug != 'CARGILL BAHÍA BLANCA'
          AND p.lug != 'VIAJE A BAHÍA BLANCA'
          AND p.lug != 'VIAJE A NECOCHEA'
          AND p.lug != 'TERMINAL BAHÍA BLANCA'
          AND p.lug != 'VITERRA BAHÍA BLANCA'
          AND p.lug != 'COFCO LIMA'
          AND p.lug != 'PTP VILLA CONSTITUCIÓN'
    """)
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


# ==========================================
# VISTA 2: FLUJO DE TAREAS (Métricas)
# ==========================================
elif st.session_state["current_page"] == "flujo":
    
    # Header adaptado para Flujo de Tareas
    st.markdown('<div class="header-container"><h1>FLUJO DE TAREAS</h1><div class="footer-right">Métricas de Rendimiento</div></div>', unsafe_allow_html=True)
    
    # Barra de navegación superior derecha para regresar
    nav_col1, nav_col2 = st.columns([4, 1])
    with nav_col2:
        if st.button("⬅️ Volver al Monitor"):
            st.session_state["current_page"] = "monitor"
            st.rerun()

    # --- FUNCIÓN DE ANILLOS ---
    def crear_anillo(df, titulo):
        try:
            df = df.copy()
            df['motivo'] = df['motivo'].astype(str).str.replace('.', '', regex=False).str.strip().str.upper()
            df = df[~df['motivo'].str.contains('VIAJE', na=False)]
            
            resumen = df.groupby('motivo').agg(Total_Hechas=('tareas_ok', 'sum')).reset_index()
            resumen = resumen[resumen['Total_Hechas'] > 0].sort_values(by='Total_Hechas', ascending=False)
            
            if resumen.empty:
                return st.write(f"Sin datos: {titulo}")

            total_general = int(resumen['Total_Hechas'].sum())

            colores_snap = {
                'CONTROL DE RUTINA': '#00A67C', 'INSTALACIÓN DEL SISTEMA': '#103F4C',
                'MANTENIMIENTO GENERAL': '#00BFB2', 'PLANIFICACIÓN Y GESTIÓN': '#000000',
                'SOPORTE AL CLIENTE': '#0F7F7D', 'AJUSTES PREELIMINARES': '#D1EBE8',
                'REPARACIONES': '#8FB3AA', 'MANTENIMIENTO ELÉCTRICO': '#778B78',
                'MANTENIMIENTO MECÁNICO': '#5F6B6A', 'SOPORTE OPERATIVO': '#837581',
                'PUESTA EN MARCHA': '#E2E4E5'
            }

            fig = px.pie(resumen, values='Total_Hechas', names='motivo', 
                         hole=0.55, color='motivo', color_discrete_map=colores_snap)
            
            fig.update_traces(
                textinfo='none', 
                hoverinfo='label+percent',
                rotation=120, 
                direction='clockwise',
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            
            fig.update_layout(
                title=dict(
                    text=titulo,
                    x=0.26,
                    y=0.88,
                    xanchor='center',
                    font=dict(size=20, color='black', family="Arial Black")
                ),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(color='black', size=14) 
                ),
                margin=dict(t=80, b=20, l=10, r=10),
                height=450,
                annotations=[dict(
                    text=f"TOTAL<br><b>{total_general}</b>", 
                    x=0.5, y=0.5, 
                    font_size=18, 
                    showarrow=False, 
                    font_color='black',
                    font_family="Arial Black"
                )]
            )
            
            fig.for_each_trace(lambda t: t.update(
                labels=[f"{n} (<b>{ (v/total_general*100):.1f}%</b>)" for n, v in zip(resumen['motivo'], resumen['Total_Hechas'])]
            ))

            return st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            pass

    # --- SECTOR INFERIOR ESTADÍSTICAS ---
    def sector_inferior_estadisticas(df_final):
        try:
            st.markdown("---")
            hoy_dt = dt_mod.datetime.now()
            hoy_f = hoy_dt.strftime('%d de Abril del %Y')

            # --- 1. DATOS PENDIENTES ---
            try:
                conn = sqlite3.connect(DB_PATH)
                df_pend = pd.read_sql("SELECT * FROM PENDIENTES", conn)
                conn.close()
            except:
                df_pend = pd.DataFrame()

            # --- 2. DATOS REALIZADAS ---
            df_realizadas = df_final.copy()
            df_realizadas['motivo'] = df_realizadas['motivo'].astype(str).str.upper()
            df_realizadas = df_realizadas[~df_realizadas['motivo'].str.contains('VIAJE', na=False)]
            
            hace_un_año = pd.Timestamp.now() - pd.DateOffset(months=12)
            df_12m = df_realizadas[df_realizadas['fec'] >= hace_un_año].copy()
            
            df_12m['Periodo'] = df_12m['fec'].dt.to_period('M')
            resumen_mes = df_12m.groupby('Periodo').agg(Total=('tareas_ok', 'sum')).reset_index()
            resumen_mes = resumen_mes[resumen_mes['Total'] >= 10].copy()

            col_izq, col_der = st.columns([1, 1])

            # --- COLUMNA IZQUIERDA: PENDIENTES ---
            with col_izq:
                st.markdown(f"<h3 style='text-align: center; color: black; font-size: 20px;'>Tareas Pendientes al {hoy_f}</h3>", unsafe_allow_html=True)
                if not df_pend.empty:
                    df_pend.columns = [c.upper() for c in df_pend.columns]
                    col_c = 'CLIENTE' if 'CLIENTE' in df_pend.columns else 'LUG'
                    resumen_p = df_pend.groupby(col_c).size().reset_index(name='Cantidad').sort_values(by='Cantidad', ascending=False)
                    
                    fig_p = px.bar(resumen_p, x=col_c, y='Cantidad', text='Cantidad', color_discrete_sequence=['#778B78'])
                    fig_p.update_layout(
                        xaxis_title=None, 
                        yaxis_title="", 
                        height=450,
                        margin=dict(t=20, b=20, l=10, r=10),
                        xaxis=dict(
                            tickangle=-90,
                            tickfont=dict(color='#000000', size=18, family="Arial Black")
                        ),
                        yaxis=dict(dtick=1, range=[0, resumen_p['Cantidad'].max() * 1.3]),
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_p.update_traces(
                        textposition='outside', 
                        textfont=dict(family="Arial Black", size=16, color='#000000'), 
                        texttemplate='%{text}'
                    )
                    st.plotly_chart(fig_p, use_container_width=True)

            # --- COLUMNA DERECHA: REALIZADAS ---
            with col_der:
                st.markdown(f"<h3 style='text-align: center; color: black; font-size: 20px;'>Tareas realizadas por mes</h3>", unsafe_allow_html=True)
                
                if not resumen_mes.empty:
                    meses_es = {
                        1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN',
                        7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'
                    }
                    resumen_mes['Mes_Label'] = resumen_mes['Periodo'].apply(lambda x: f"{meses_es[x.month]} {str(x.year)[2:]}")
                    
                    max_m = resumen_mes['Total'].max()
                    fig_m = px.bar(resumen_mes, x='Mes_Label', y='Total', text='Total', color_discrete_sequence=['#00A67C'])
                    fig_m.update_layout(
                        xaxis_title=None, 
                        yaxis_title=None, 
                        height=450,
                        margin=dict(t=20, b=100, l=10, r=10),
                        xaxis=dict(
                            tickangle=-90,
                            tickfont=dict(color='#000000', size=16, family="Arial Black")
                        ),
                        yaxis=dict(dtick=50 if max_m > 100 else 10, range=[0, max_m * 1.3]),
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_m.update_traces(
                        textposition='outside', 
                        textfont=dict(family="Arial Black", size=16, color='#000000'), 
                        texttemplate='%{text}'
                    )
                    st.plotly_chart(fig_m, use_container_width=True)
                else:
                    st.info("No hay meses con más de 10 tareas realizadas.")
        except Exception as e:
            st.error(f"Error en sector inferior: {e}")

    # --- LÓGICA DE CARGA Y PROCESAMIENTO PARA ANILLOS ---
    if not os.path.exists(DB_PATH):
        st.error(f"Base de datos no encontrada.")
    else:
        conn = sqlite3.connect(DB_PATH)
        df_p = pd.read_sql("SELECT id, fec, lug FROM planif", conn)
        df_o = pd.read_sql("SELECT id_pl, tareas, motivo FROM ordenes", conn)
        conn.close()

        df_final = pd.merge(df_o, df_p, left_on='id_pl', right_on='id')
        df_final['fec'] = pd.to_datetime(df_final['fec'], dayfirst=True, errors='coerce')
        df_final = df_final.dropna(subset=['fec'])
        df_final['tareas_ok'] = df_final['tareas'].apply(lambda x: str(x).upper().count('[X]') if x else 0)

        hoy = pd.Timestamp.now().normalize()
        df_año = df_final[df_final['fec'].dt.year == hoy.year]
        df_mes = df_final[(df_final['fec'].dt.month == hoy.month) & (df_final['fec'].dt.year == hoy.year)]
        
        # Lógica dinámica semanal
        df_semana = df_final[df_final['fec'].dt.isocalendar().week == hoy.isocalendar().week]
        df_semana_limpio = df_semana.copy()
        df_semana_limpio['motivo'] = df_semana_limpio['motivo'].astype(str).str.replace('.', '', regex=False).str.strip().str.upper()
        df_semana_limpio = df_semana_limpio[~df_semana_limpio['motivo'].str.contains('VIAJE', na=False)]
        
        total_semana_actual = df_semana_limpio['tareas_ok'].sum()
        
        if total_semana_actual == 0:
            semana_pasada_num = (hoy - pd.DateOffset(weeks=1)).isocalendar().week
            año_semana_pasada = (hoy - pd.DateOffset(weeks=1)).isocalendar().year
            df_semana = df_final[(df_final['fec'].dt.isocalendar().week == semana_pasada_num) & (df_final['fec'].dt.isocalendar().year == año_semana_pasada)]
            titulo_semana = "SEMANA PASADA"
        else:
            titulo_semana = "ESTA SEMANA"

        # RENDERIZADO DE LOS ANILLOS
        c1, c2, c3 = st.columns(3)
        with c1: 
            crear_anillo(df_año, "AÑO ACTUAL")
        with c2: 
            crear_anillo(df_mes, "MES ACTUAL")
        with c3: 
            crear_anillo(df_semana, titulo_semana)

        # RENDERIZADO DE LAS ESTADÍSTICAS INFERIORES
        sector_inferior_estadisticas(df_final)
