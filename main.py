import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA (SÓLO AQUÍ) ---
st.set_page_config(
    layout="wide", 
    page_title="SNAP - Sistema Operativo",
    page_icon="🟢"
)

# --- VERIFICACIÓN DE CONTRASEÑA ---
def check_password():
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

# --- CONTROL DE NAVEGACIÓN MULTI-PÁGINA ---
pag_monitor = st.Page("monitor.py", title="Monitor de Operaciones", icon="📊")
pag_flujo = st.Page("flujo_de_trabajo.py", title="Flujo de Tareas", icon="📈")

pg = st.navigation([pag_monitor, pag_flujo], position="hidden")

if "current_page" not in st.session_state:
    st.session_state["current_page"] = pag_monitor

pg.run()