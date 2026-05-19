import pandas as pd
import sqlite3
import streamlit as st
import os
import plotly.express as px
import datetime

def mostrar_graficos():
    # --- ESTILOS CSS PARA PASAR A PANTALLA COMPLETA ---
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
        .header-flujo { background-color: #1db978; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="header-flujo"><h1>FLUJO DE TAREAS</h1></div>', unsafe_allow_html=True)

    # --- BOTÓN RETORNO MODIFICADO ---
    col_b1, col_b2 = st.columns([4, 1])
    with col_b2:
        if st.button("⬅️ Volver al Monitor", use_container_width=True):
            st.session_state["seccion_activa"] = "monitor"
            st.rerun()

    st.markdown("---")

    db_path = "gestion_snap_v5.db"

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
                    text=titulo, x=0.26, y=0.88, xanchor='center',
                    font=dict(size=20, color='black', family="Arial Black")
                ),
                showlegend=True,
                legend=dict(
                    orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05,
                    font=dict(color='black', size=14) 
                ),
                margin=dict(t=80, b=20, l=10, r=10),
                height=450,
                annotations=[dict(
                    text=f"TOTAL<br><b>{total_general}</b>", x=0.5, y=0.5, 
                    font_size=18, showarrow=False, font_color='black', font_family="Arial Black"
                )]
            )
            
            fig.for_each_trace(lambda t: t.update(
                labels=[f"{n} (<b>{ (v/total_general*100):.1f}%</b>)" for n, v in zip(resumen['motivo'], resumen['Total_Hechas'])]
            ))

            return st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    # --- SECTOR INFERIOR: ESTADÍSTICAS ---
    def sector_inferior_estadisticas(df_final):
        try:
            st.markdown("---")
            hoy_dt = datetime.datetime.now()
            hoy_f = hoy_dt.strftime('%d de Abril del %Y')

            conn = sqlite3.connect(db_path)
            try:
                df_pend = pd.read_sql("SELECT * FROM PENDIENTES", conn)
            except:
                df_pend = pd.DataFrame()
            conn.close()

            df_realizadas = df_final.copy()
            df_realizadas['motivo'] = df_realizadas['motivo'].astype(str).str.upper()
            df_realizadas = df_realizadas[~df_realizadas['motivo'].str.contains('VIAJE', na=False)]
            
            hace_un_año = pd.Timestamp.now() - pd.DateOffset(months=12)
            df_12m = df_realizadas[df_realizadas['fec'] >= hace_un_año].copy()
            
            df_12m['Periodo'] = df_12m['fec'].dt.to_period('M')
            resumen_mes = df_12m.groupby('Periodo').agg(Total=('tareas_ok', 'sum')).reset_index()
            resumen_mes = resumen_mes[resumen_mes['Total'] >= 10].copy()

            col_izq, col_der = st.columns([1, 1])

            with col_izq:
                st.markdown(f"<h3 style='text-align: center; color: black; font-size: 20px;'>Tareas Pendientes al {hoy_f}</h3>", unsafe_allow_html=True)
                if not df_pend.empty:
                    df_pend.columns = [c.upper() for c in df_pend.columns]
                    col_c = 'CLIENTE' if 'CLIENTE' in df_pend.columns else 'LUG'
                    resumen_p = df_pend.groupby(col_c).size().reset_index(name='Cantidad').sort_values(by='Cantidad', ascending=False)
                    
                    fig_p = px.bar(resumen_p, x=col_c, y='Cantidad', text='Cantidad', color_discrete_sequence=['#778B78'])
                    fig_p.update_layout(
                        xaxis_title=None, yaxis_title="", height=450,
                        margin=dict(t=20, b=20, l=10, r=10),
                        xaxis=dict(tickangle=-90, tickfont=dict(color='#000000', size=18, family="Arial Black")),
                        yaxis=dict(dtick=1, range=[0, resumen_p['Cantidad'].max() * 1.3]),
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_p.update_traces(textposition='outside', textfont=dict(family="Arial Black", size=16, color='#000000'), texttemplate='%{text}')
                    st.plotly_chart(fig_p, use_container_width=True)

            with col_der:
                st.markdown(f"<h3 style='text-align: center; color: black; font-size: 20px;'>Tareas realizadas por mes</h3>", unsafe_allow_html=True)
                if not resumen_mes.empty:
                    meses_es = {1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'}
                    resumen_mes['Mes_Label'] = resumen_mes['Periodo'].apply(lambda x: f"{meses_es[x.month]} {str(x.year)[2:]}")
                    
                    max_m = resumen_mes['Total'].max()
                    fig_m = px.bar(resumen_mes, x='Mes_Label', y='Total', text='Total', color_discrete_sequence=['#00A67C'])
                    fig_m.update_layout(
                        xaxis_title=None, yaxis_title=None, height=450,
                        margin=dict(t=20, b=100, l=10, r=10),
                        xaxis=dict(tickangle=-90, tickfont=dict(color='#000000', size=16, family="Arial Black")),
                        yaxis=dict(dtick=50 if max_m > 100 else 10, range=[0, max_m * 1.3]),
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_m.update_traces(textposition='outside', textfont=dict(family="Arial Black", size=16, color='#000000'), texttemplate='%{text}')
                    st.plotly_chart(fig_m, use_container_width=True)
        except Exception as e:
            st.error(f"Error en sector inferior: {e}")

    # --- LÓGICA DE CARGA Y EJECUCIÓN ---
    if not os.path.exists(db_path):
        st.error(f"Base de datos no encontrada.")
    else:
        conn = sqlite3.connect(db_path)
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

        c1, c2, c3 = st.columns(3)
        with c1: crear_anillo(df_año, "AÑO ACTUAL")
        with c2: crear_anillo(df_mes, "MES ACTUAL")
        with c3: crear_anillo(df_semana, titulo_semana)

        sector_inferior_estadisticas(df_final)