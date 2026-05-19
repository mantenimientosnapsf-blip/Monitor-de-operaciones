import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ÚNICA ---
st.set_page_config(
    layout="wide", 
    page_title="SNAP - Sistema Operativo",
    page_icon="🟢"
)

# --- VERIFICACIÓN DE CONTRASEÑA ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    if st.query_params.get("auth") == "authorized":
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
        if st.button("Ingresar", use_container_width=True):
            if password == "Snap3478":
                st.session_state["password_correct"] = True
                st.query_params["auth"] = "authorized"
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    return False

if not check_password():
    st.stop()

# --- CONTROL DE NAVEGACIÓN TOTALMENTE AISLADO ---
if "seccion_activa" not in st.session_state:
    st.session_state["seccion_activa"] = "monitor"

# Importación y ejecución controlada por bloques lógicos puros
if st.session_state["seccion_activa"] == "monitor":
    import monitor
    monitor.mostrar_monitor()
else:
    import flujo_de_trabajo
    flujo_de_trabajo.mostrar_graficos()