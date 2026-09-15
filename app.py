import streamlit as st
import pandas as pd
from sqlalchemy import text
import unicodedata

# ==============================================================================
# CONEXIÓN A LA BASE DE DATOS LOCAL (XAMPP / MYSQL)
# ==============================================================================
# Conexión única y limpia para Supabase en la nube y en tu PC
conn = st.connection("supabase", type="sql")

# ==============================================================================
# FUNCIÓN AUXILIAR PARA NORMALIZAR TEXTOS (ELIMINAR TILDES Y ACENTOS)
# ==============================================================================
def normalizar_texto(texto):
    """
    Toma cualquier texto, elimina tildes y caracteres especiales, y lo pasa a minúsculas
    para evitar errores de coincidencia en las consultas.
    """
    if not texto:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).strip().lower()

# ==============================================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA Y ESTILOS VISUALES
# ==============================================================================
# Configuramos la pestaña del navegador, el título, el ícono y el diseño ancho ('wide')
st.set_page_config(
    page_title="Sistema de Apuestas Deportivas - YANESBET",
    page_icon="⚽",
    layout="wide"
)

# Inyectamos estilos CSS personalizados mediante etiquetas HTML para estilizar la interfaz
st.markdown("""
    <style>
        .stApp {
            background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.85)), 
                              url('https://images.unsplash.com/photo-1518091043644-c1d4457512c6?q=80&w=1931&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #e0e0e0;
        }
        
        .stApp::before {
            content: "YANESBET";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-25deg);
            font-size: 10rem;
            font-weight: 900;
            color: rgba(255, 255, 255, 0.03);
            z-index: 0;
            pointer-events: none;
            white-space: nowrap;
        }

        h1 {
            text-align: center !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
            font-size: 2.2rem !important;
        }

        h2, h3, .stMarkdown p {
            text-align: center !important;
            color: #f1f1f1 !important;
        }

        label.st-bp, div[data-baseweb="select"] > div, .stSelectbox label, .stDateInput label, .stTextInput label {
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: #f1f1f1 !important;
        }

        div[data-baseweb="select"] > div {
            background-color: rgba(25, 25, 25, 0.85) !important;
            border: 2px solid rgba(255, 215, 0, 0.4) !important;
            border-radius: 10px !important;
            color: white !important;
        }

        input {
            background-color: rgba(25, 25, 25, 0.85) !important;
            border-radius: 8px !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        .stForm {
            background: rgba(15, 15, 15, 0.75) !important;
            padding: 25px !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 215, 0, 0.3) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
            backdrop-filter: blur(8px) !important;
        }

        div.stButton > button {
            background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%) !important;
            color: white !important;
            font-weight: bold;
            border-radius: 10px;
            border: none;
            width: 100%;
            padding: 10px;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #45a049 0%, #2e7d32 100%) !important;
            color: white;
        }

        .stFormSubmitButton > button {
            width: 100% !important;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
            color: #000000 !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
            padding: 12px 20px !important;
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(255, 165, 0, 0.4) !important;
            transition: all 0.3s ease-in-out !important;
        }
        .stFormSubmitButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6) !important;
            background: linear-gradient(135deg, #ffdf33 0%, #ffb733 100%) !important;
        }

        .footer {
            position: relative;
            width: 100%;
            background-color: rgba(10, 10, 10, 0.9);
            color: #cccccc;
            text-align: center;
            padding: 15px;
            margin-top: 50px;
            border-top: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 10px;
            font-size: 0.9rem;
        }
        .footer span {
            color: #FFD700;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)



# ==============================================================================
# 1. SISTEMA DE AUTENTICACIÓN CONECTADO A SUPABASE
# ==============================================================================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'cambio_pendiente' not in st.session_state:
    st.session_state['cambio_pendiente'] = False
if 'usuario_temporal' not in st.session_state:
    st.session_state['usuario_temporal'] = None

def mostrar_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 YANESBET - Acceso Restringido</h1>", unsafe_allow_html=True)
        
        if st.session_state['cambio_pendiente']:
            st.warning("⚠️ Es tu primer ingreso. Por seguridad, debes actualizar tu contraseña.")
            st.info("Requisitos: Mínimo 6 caracteres, letras (mayúsculas/minúsculas), números y sin caracteres especiales.")
            
            nueva_pass = st.text_input("Nueva Contraseña", type="password", key="np1")
            conf_pass = st.text_input("Confirmar Nueva Contraseña", type="password", key="np2")
            
                    if st.button("Actualizar y Entrar", use_container_width=True):
            tiene_letras = any(c.isalpha() for c in nueva_pass)
            tiene_numeros = any(c.isdigit() for c in nueva_pass)
            tiene_especiales = not nueva_pass.isalnum()

            if len(nueva_pass) < 6:
                st.error("❌ Mínimo 6 caracteres.")
            elif not (tiene_letras and tiene_numeros):
                st.error("❌ Debe contener letras y números.")
            elif tiene_especiales:
                st.error("❌ No utilices símbolos especiales o espacios.")
            elif nueva_pass != conf_pass:
                st.error("❌ Las contraseñas no coinciden.")
            else:
                try:
                    from sqlalchemy import text
                    with conn.connect() as connection:
                        connection.execute(
                            text(f"UPDATE usuarios_sistema SET password = '{nueva_pass}', cambio_pendiente = FALSE WHERE username = '{st.session_state['usuario_temporal']}'")
                        )
                        connection.commit()
                    st.success("¡Contraseña actualizada!")
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_actual'] = st.session_state['usuario_temporal']
                    st.session_state['cambio_pendiente'] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error en BD: {e}")
                    



    else:
    st.markdown("<p style='text-align: center; color: #8b949e;'>Ingrese sus credenciales del proyecto.</p>", unsafe_allow_html=True)
    usuario = st.text_input("Usuario", key="lg1")
    password = st.text_input("Contraseña", type="password", key="lg2")
            
    if st.button("Ingresar al Sistema", use_container_width=True):
try:
query = f"SELECT * FROM usuarios_sistema WHERE username = '{usuario}' AND password = '{password}'"
df_user = conn.query(query, ttl=0)
                    
    if not df_user.empty:
          debe_cambiar=df_user.iloc[0]ñ['cambio_pendiente']
      if debe_cambiar:
      st.session_state['cambio_pendiente'] = True
      st.session_state['usuario_temporal'] = usuario
      st.rerun()
 else:
   st.session_state['autenticado'] = True
   st.session_state['usuario_actual'] = usuario  
   st.rerun()                            
  
 else:
     st.error("❌ Usuario o contraseña incorrectos.")
     except Exception as e:
     st.error(f"Error de conexión: {e}")


        
        # PANTALLA 1: Login normal consultando Supabase
        else:
            st.markdown("<p style='text-align: center; color: #8b949e;'>Ingrese sus credenciales del proyecto.</p>", unsafe_allow_html=True)
            with st.form("form_login"):
                usuario = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                submit_login = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
                
                if submit_login:
                    try:
                        query = f"SELECT * FROM usuarios_sistema WHERE username = '{usuario}' AND password = '{password}'"
                        df_user = conn.query(query, ttl=0)
                        
                        if not df_user.empty:
                            debe_cambiar = df_user.iloc[0]['cambio_pendiente']
                            
                            if debe_cambiar:
                                st.session_state['cambio_pendiente'] = True
                                st.session_state['usuario_temporal'] = usuario
                                st.rerun()
                            else:
                                st.session_state['autenticado'] = True
                                st.session_state['usuario_actual'] = usuario
                                st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos.")
                    except Exception as e:
                        st.error(f"Error de conexión al verificar el usuario: {e}")


        
        # PANTALLA 1: Login normal consultando Supabase
        else:
            st.markdown("<p style='text-align: center; color: #8b949e;'>Ingrese sus credenciales del proyecto.</p>", unsafe_allow_html=True)
            with st.form("form_login"):
                usuario = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                submit_login = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
                
                if submit_login:
                    try:
                        # Consultamos el usuario en la base de datos
                        query = f"SELECT * FROM usuarios_sistema WHERE username = '{usuario}' AND password = '{password}'"
                        df_user = conn.query(query, ttl=0)
                        
                        if not df_user.empty:
                            debe_cambiar = df_user.iloc[0]['cambio_pendiente']
                            
                            if debe_cambiar:
                                st.session_state['cambio_pendiente'] = True
                                st.session_state['usuario_temporal'] = usuario
                                st.rerun()
                            else:
                                st.session_state['autenticado'] = True
                                st.session_state['usuario_actual'] = usuario
                                st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos.")
                    except Exception as e:
                        st.error(f"Error de conexión al verificar el usuario: {e}")

# Bloque de parada de seguridad
if not st.session_state['autenticado']:
    mostrar_login()
    st.stop()







# ==============================================================================
# BARRA LATERAL DE NAVEGACIÓN GLOBAL (SIDEBAR)
# ==============================================================================
st.sidebar.title("⚽ Menú YANESBET")
st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 Conectado como: **{st.session_state.get('usuario_actual', '').capitalize()}**")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

opciones_menu = [
    "🏠 Inicio", 
    "📝 Registrar Estadísticas", 
    "📊 Visualizar Base de Datos", 
    "⚔️ Comparar Equipos", 
    "📈 Calculadora y Probabilidades"
]

indice_actual = 0
if st.session_state['pagina'] == 'formulario_equipos':
    indice_actual = 1
elif st.session_state['pagina'] == 'visualizador':
    indice_actual = 2
elif st.session_state['pagina'] == 'comparar_equipos':
    indice_actual = 3
elif st.session_state['pagina'] == 'calculadora':
    indice_actual = 4

menu_opcion = st.sidebar.radio("Selecciona una opción:", opciones_menu, index=indice_actual)

if menu_opcion == "🏠 Inicio":
    st.session_state['pagina'] = 'inicio'
elif menu_opcion == "📝 Registrar Estadísticas":
    st.session_state['pagina'] = 'formulario_equipos'
elif menu_opcion == "📊 Visualizar Base de Datos":
    st.session_state['pagina'] = 'visualizador'
elif menu_opcion == "⚔️ Comparar Equipos":
    st.session_state['pagina'] = 'comparar_equipos'
elif menu_opcion == "📈 Calculadora y Probabilidades":
    st.session_state['pagina'] = 'calculadora'

# ==============================================================================
# VISTA 1: MENÚ PRINCIPAL DEL SISTEMA
# ==============================================================================
def inicio():
    st.markdown("<h1>Sistema de Apuestas Deportivas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0; font-size: 1.1rem;'>Bienvenido al sistema de análisis y registro de estadísticas de <b>YANESBET</b>.</p>", unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("Ir al Formulario de Equipos"):
            st.session_state['pagina'] = 'formulario_equipos'
            st.rerun()

# ==============================================================================
# VISTA 2: CARGA DEL FORMULARIO DE PARTIDOS Y CONSULTAS A LA BASE DE DATOS
# ==============================================================================
def formulario_equipos():
    st.markdown("<h3>Registro de Estadísticas de Partidos</h3>", unsafe_allow_html=True)
    
    ultimo_equipo = st.session_state.get('ultimo_equipo', '')
    
    try:
        query_ligas = "SELECT id, nombre FROM ligas ORDER BY id ASC"
        df_ligas = conn.query(query_ligas, ttl=0)
    except Exception as e:
        st.error(f"Error detallado de conexión con Supabase (Ligas): {e}")
        return

    ligas = df_ligas.to_dict('records')
    liga_nombres = {liga['id']: liga['nombre'] for liga in ligas}
    
    liga_id_seleccionada = st.selectbox(
        "Selecciona la Competición / Liga:",
        options=list(liga_nombres.keys()),
        format_func=lambda x: liga_nombres[x],
        key="form_liga_select"
    )
    
    equipos = []
    if liga_id_seleccionada:
        liga_id_int = int(liga_id_seleccionada)
        
        mapeo_copas = {
            10: 1, 11: 1, 12: 2, 13: 2, 14: 2, 
            15: 3, 16: 3, 17: 4, 18: 4, 19: 5, 20: 5
        }
        id_a_consultar = mapeo_copas.get(liga_id_int, liga_id_int)
        
        query_equipos = """
            SELECT MIN(id) AS id, nombre, liga_id 
            FROM equipos 
            WHERE liga_id = :liga_id 
            GROUP BY nombre, liga_id
            ORDER BY nombre ASC
        """
        try:
            df_equipos = conn.query(query_equipos, params={"liga_id": id_a_consultar}, ttl=0)
            equipos = df_equipos.to_dict('records')
        except Exception as e:
            st.error(f"Error detallado de conexión con Supabase (Equipos): {e}")

    nombres_equipos = [eq['nombre'] for eq in equipos] if equipos else []
    
    default_index = 0
    if ultimo_equipo in nombres_equipos:
        default_index = nombres_equipos.index(ultimo_equipo)

    equipo_analizado = st.selectbox(
        "Equipo Analizado:", 
        options=nombres_equipos, 
        index=default_index if nombres_equipos else 0,
        key="form_equipo_analizado"
    )
    
    nombres_rivales = [eq for eq in nombres_equipos if eq != equipo_analizado]
    
    with st.form("form_estadisticas"):
        fecha_partido = st.date_input("Fecha del Partido")
        
        rival = st.selectbox(
            "Rival", 
            options=nombres_rivales if nombres_rivales else nombres_equipos
        )
        
        condicion = st.selectbox("Condición", options=["Local", "Visitante"])
        competicion_texto = liga_nombres.get(liga_id_seleccionada, "")
        competicion = st.text_input("Competición (Texto)", value=competicion_texto)
        
        col1, col2 = st.columns(2)
        with col1:
            goles_favor = st.number_input("Goles a Favor (Totales)", min_value=0, step=1)
            goles_contra = st.number_input("Goles en Contra", min_value=0, step=1)
            goles_favor_1t = st.number_input("Goles a Favor - 1er Tiempo", min_value=0, step=1)
            goles_favor_2t = st.number_input("Goles a Favor - 2do Tiempo", min_value=0, step=1)
            tiros_totales = st.number_input("Tiros Totales", min_value=0, step=1)
            tiros_a_porta = st.number_input("Tiros a Puerta", min_value=0, step=1)
            tiros_al_palo = st.number_input("Tiros al Palo", min_value=0, step=1)
        
        with col2:
            corners = st.number_input("Saques de Esquina (Corners)", min_value=0, step=1)
            atajadas = st.number_input("Atajadas del Portero", min_value=0, step=1)
            tarjetas_amarillas = st.number_input("Tarjetas Amarillas", min_value=0, step=1)
            tarjetas_rojas = st.number_input("Tarjetas Rojas", min_value=0, step=1)
            faltas_cometidas = st.number_input("Faltas Cometidas", min_value=0, step=1)
            fueras_de_juego = st.number_input("Fueras de Juego", min_value=0, step=1)
            
            st.write("")
            st.write("")
            submitted = st.form_submit_button("Guardar Estadísticas")




        
        if submitted:
            # --- PEGAS LAS VALIDACIONES AQUÍ ---
            errores = []
            if tiros_a_puerta > tiros_totales:
                errores.append("⚠️ Los 'Tiros a Puerta' no pueden ser mayores que los 'Tiros Totales'.")
            
            if errores:
                st.error("Se detectaron errores en los datos:")
                for err in errores:
                    st.warning(err)
            else:
                # --- Y AQUÍ DEJAS TU CÓDIGO ORIGINAL QUE YA TENÍAS ---
                if goles_favor > goles_contra:
                    resultado_equipo = 'Victoria'
                # ... (lo demás que ya tenías)


            if goles_favor > goles_contra:
                resultado_equipo = 'Victoria'
            elif goles_favor < goles_contra:
                resultado_equipo = 'Derrota'
            else:
                resultado_equipo = 'Empate'
                
            sql_insert = """
                INSERT INTO estadisticas_equipos (
                    equipo_analizado, fecha_partido, rival, condicion, competicion,
                    resultado_equipo, goles_favor, goles_contra, goles_favor_1t, goles_favor_2t,
                    tiros_totales, tiros_a_puerta, tiros_al_palo, corners, atajadas,
                    tarjetas_amarillas, tarjetas_rojas, faltas_cometidas, fueras_de_juego
                ) VALUES (:eq, :fec, :riv, :cond, :comp, :res, :gf, :gc, :gf1t, :gf2t, :tt, :tap, :tp, :cor, :ata, :ta, :tr, :fal, :fdej)
            """
            
            try:
                with conn.session as s:
                    s.execute(
                        text(sql_insert),
                        {
                            "eq": equipo_analizado, "fec": str(fecha_partido), "riv": rival, 
                            "cond": condicion, "comp": competicion, "res": resultado_equipo, 
                            "gf": goles_favor, "gc": goles_contra, "gf1t": goles_favor_1t, "gf2t": goles_favor_2t,
                            "tt": tiros_totales, "tap": tiros_a_porta, "tp": tiros_al_palo, "cor": corners, 
                            "ata": atajadas, "ta": tarjetas_amarillas, "tr": tarjetas_rojas, 
                            "fal": faltas_cometidas, "fdej": fueras_de_juego
                        }
                    )
                    s.commit()
                st.success("¡Estadísticas guardadas con éxito en el sistema!")
                st.session_state['ultimo_equipo'] = equipo_analizado
            except Exception as e:
                st.error(f"Error detallado al guardar los datos en Supabase: {e}")

# ==============================================================================
# VISTA 3: VISUALIZADOR GENERAL DE LA BASE DE DATOS
# ==============================================================================
def visualizador_base_datos():
    st.markdown("<h2>Monitoreo de Base de Datos - Estadísticas Registradas</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0;'>Consulta en tiempo real todos los registros almacenados en Supabase.</p>", unsafe_allow_html=True)
    
    query_datos = "SELECT * FROM estadisticas_equipos ORDER BY id DESC"
    
    try:
        df_registros = conn.query(query_datos, ttl=0)
        
        if not df_registros.empty:
            total_partidos = len(df_registros)
            st.metric(label="Total de Partidos Registrados", value=total_partidos)
            st.dataframe(df_registros, use_container_width=True)
        else:
            st.info("No hay registros guardados todavía en la base de datos.")
            
    except Exception as e:
        st.error(f"Error detallado de conexión con Supabase (Visualizador): {e}")

# ==============================================================================
# VISTA 4: COMPARADOR DE EQUIPOS
# ==============================================================================
def comparar_equipos():
    st.markdown("<h2>⚔️ Comparativa Directa de Equipos por Competición</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0;'>Filtra por competición superior y selecciona dos equipos para contraponer sus promedios e historiales.</p>", unsafe_allow_html=True)
    
    try:
        query_ligas = "SELECT id, nombre FROM ligas ORDER BY id ASC"
        df_ligas = conn.query(query_ligas, ttl=0)
    except Exception as e:
        st.error(f"Error detallado de conexión con Supabase (Comparativa Ligas): {e}")
        return
    
    if df_ligas.empty:
        st.info("No hay ligas registradas en la base de datos.")
        return
        
    ligas_dict = {row['nombre']: row['id'] for index, row in df_ligas.iterrows()}
    nombres_ligas = list(ligas_dict.keys())
    
    mapeo_copas = {
        10: 1, 11: 1, 12: 2, 13: 2, 14: 2, 
        15: 3, 16: 3, 17: 4, 18: 4, 19: 5, 20: 5
    }
    
    col_eq1, col_eq2 = st.columns(2)
    
    with col_eq1:
        st.markdown("<h4>Equipo 1</h4>", unsafe_allow_html=True)
        liga_1_nombre = st.selectbox("Competición / Liga (Equipo 1):", options=nombres_ligas, key="liga_1_sel")
        liga_1_id_raw = ligas_dict[liga_1_nombre]
        liga_1_id_consultar = mapeo_copas.get(liga_1_id_raw, liga_1_id_raw)
        
        query_eq1 = "SELECT nombre FROM equipos WHERE liga_id = :lid ORDER BY nombre ASC"
        try:
            df_eq1 = conn.query(query_eq1, params={"lid": liga_1_id_consultar}, ttl=0)
        except Exception as e:
            st.error(f"Error detallado de conexión con Supabase (Eq 1): {e}")
            df_eq1 = pd.DataFrame()
        lista_equipos_1 = df_eq1['nombre'].tolist() if not df_eq1.empty else []
        
        equipo_1 = st.selectbox("Selecciona el Equipo 1:", options=lista_equipos_1, key="eq_1_sel") if lista_equipos_1 else None
        
    with col_eq2:
        st.markdown("<h4>Equipo 2</h4>", unsafe_allow_html=True)
        liga_2_nombre = st.selectbox("Competición / Liga (Equipo 2):", options=nombres_ligas, key="liga_2_sel")
        liga_2_id_raw = ligas_dict[liga_2_nombre]
        liga_2_id_consultar = mapeo_copas.get(liga_2_id_raw, liga_2_id_raw)
        
        query_eq2 = "SELECT nombre FROM equipos WHERE liga_id = :lid ORDER BY nombre ASC"
        try:
            df_eq2 = conn.query(query_eq2, params={"lid": liga_2_id_consultar}, ttl=0)
        except Exception as e:
            st.error(f"Error detallado de conexión con Supabase (Eq 2): {e}")
            df_eq2 = pd.DataFrame()
        lista_equipos_2 = df_eq2['nombre'].tolist() if not df_eq2.empty else []
        
        equipo_2 = st.selectbox("Selecciona el Equipo 2:", options=lista_equipos_2, key="eq_2_sel") if lista_equipos_2 else None
    
    if not equipo_1 or not equipo_2:
        return
        
    if equipo_1 == equipo_2:
        st.warning("⚠️ Has seleccionado el mismo equipo en ambos lados. Por favor elige clubes distintos para comparar.")
        return
        
    try:
        query_match = "SELECT * FROM estadisticas_equipos ORDER BY id DESC"
        df_todos_partidos = conn.query(query_match, ttl=0)
    except Exception as e:
        st.error(f"Error detallado de conexión con Supabase (Partidos Comparativa): {e}")
        return
    
    def filtrar_partidos_equipo(df, nombre_equipo):
        if df.empty:
            return pd.DataFrame()
        norm_sel = normalizar_texto(nombre_equipo)
        palabras_clave = [p for p in norm_sel.split() if len(p) > 2]
        
        def coincide(val):
            val_norm = normalizar_texto(val)
            if norm_sel in val_norm or val_norm in norm_sel:
                return True
            for p in palabras_clave:
                if p in val_norm:
                    return True
            return False
            
        return df[df['equipo_analizado'].apply(coincide)]

    df_match_1 = filtrar_partidos_equipo(df_todos_partidos, equipo_1)
    df_match_2 = filtrar_partidos_equipo(df_todos_partidos, equipo_2)
    
    st.write("")
    st.markdown("---")
    st.markdown(f"<h3>📊 Comparativa de Promedios: {equipo_1} vs {equipo_2}</h3>", unsafe_allow_html=True)
    
    def calcular_promedios(df):
        if df.empty:
            return {
                "partidos": 0, "gf": 0.0, "gc": 0.0, "gf1t": 0.0, "gf2t": 0.0,
                "tt": 0.0, "tap": 0.0, "corners": 0.0, "amarillas": 0.0, "faltas": 0.0
            }
        return {
            "partidos": len(df),
            "gf": round(df['goles_favor'].mean(), 2),
            "gc": round(df['goles_contra'].mean(), 2),
            "gf1t": round(df['goles_favor_1t'].mean(), 2),
            "gf2t": round(df['goles_favor_2t'].mean(), 2),
            "tt": round(df['tiros_totales'].mean(), 2),
            "tap": round(df['tiros_a_puerta'].mean(), 2),
            "corners": round(df['corners'].mean(), 2),
            "amarillas": round(df['tarjetas_amarillas'].mean(), 2),
            "faltas": round(df['faltas_cometidas'].mean(), 2)
        }
        
    p1 = calcular_promedios(df_match_1)
    p2 = calcular_promedios(df_match_2)
    
    df_comparativa = pd.DataFrame({
        "Métrica Estadística": [
            "Partidos Registrados", "Promedio Goles a Favor", "Promedio Goles en Contra", 
            "Goles Favor (1er Tiempo)", "Goles Favor (2do Tiempo)",
            "Tiros Totales", "Tiros a Puerta", "Saques de Esquina (Corners)", 
            "Tarjetas Amarillas", "Faltas Cometidas"
        ],
        str(equipo_1): [
            p1["partidos"], p1["gf"], p1["gc"], p1["gf1t"], p1["gf2t"],
            p1["tt"], p1["tap"], p1["corners"], p1["amarillas"], p1["faltas"]
        ],
        str(equipo_2): [
            p2["partidos"], p2["gf"], p2["gc"], p2["gf1t"], p2["gf2t"],
            p2["tt"], p2["tap"], p2["corners"], p2["amarillas"], p2["faltas"]
        ]
    })
    
    st.dataframe(df_comparativa, use_container_width=True, hide_index=True)
    
    st.write("")
    st.markdown("---")
    
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        st.markdown(f"<h4>Historial: {equipo_1}</h4>", unsafe_allow_html=True)
        if not df_match_1.empty:
            st.dataframe(df_match_1[['fecha_partido', 'rival', 'condicion', 'resultado_equipo', 'goles_favor', 'goles_contra']], use_container_width=True, hide_index=True)
        else:
            st.info(f"No hay partidos registrados todavía para {equipo_1}.")
            
    with col_hist2:
        st.markdown(f"<h4>Historial: {equipo_2}</h4>", unsafe_allow_html=True)
        if not df_match_2.empty:
            st.dataframe(df_match_2[['fecha_partido', 'rival', 'condicion', 'resultado_equipo', 'goles_favor', 'goles_contra']], use_container_width=True, hide_index=True)
        else:
            st.info(f"No hay partidos registrados todavía para {equipo_2}.")

# ==============================================================================
# VISTA 5: CALCULADORA Y PROBABILIDADES AVANZADAS (COMPLETA CON TODAS LAS MÉTRICAS)
# ==============================================================================
def calculadora_probabilidades():
    st.markdown("<h2>📈 Calculadora Avanzada de Probabilidades y Mercados</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0;'>Analiza las probabilidades de gol por tiempo, mercados específicos y todas las estadísticas detalladas.</p>", unsafe_allow_html=True)
    
    try:
        query_equipos_bd = "SELECT DISTINCT equipo_analizado FROM estadisticas_equipos ORDER BY equipo_analizado ASC"
        df_nombres = conn.query(query_equipos_bd, ttl=0)
    except Exception as e:
        st.error(f"Error detallado de conexión con Supabase (Calculadora Nombres): {e}")
        return
    
    if df_nombres.empty:
        st.info("No hay datos suficientes para ejecutar cálculos de probabilidad.")
        return
        
    lista_equipos = df_nombres['equipo_analizado'].tolist()
    
    equipo_sel = st.selectbox("Selecciona un equipo para evaluar sus tendencias de apuestas:", options=lista_equipos)
    
    try:
        query_match = "SELECT * FROM estadisticas_equipos"
        df_todos = conn.query(query_match, ttl=0)
    except Exception as e:
        st.error(f"Error detallado de conexión con Supabase (Calculadora Partidos): {e}")
        return
    
    if not df_todos.empty:
        norm_sel = normalizar_texto(equipo_sel)
        palabras_clave = [p for p in norm_sel.split() if len(p) > 2]
        
        def coincide(val):
            val_norm = normalizar_texto(val)
            if norm_sel in val_norm or val_norm in norm_sel:
                return True
            for p in palabras_clave:
                if p in val_norm:
                    return True
            return False
            
        df_t = df_todos[df_todos['equipo_analizado'].apply(coincide)]
    else:
        df_t = pd.DataFrame()
    
    if df_t.empty:
        st.warning("Este equipo no cuenta con partidos registrados.")
        return
        
    total_matches = len(df_t)
    
    # Conteo de resultados
    victorias = len(df_t[df_t['resultado_equipo'] == 'Victoria'])
    empates = len(df_t[df_t['resultado_equipo'] == 'Empate'])
    derrotas = len(df_t[df_t['resultado_equipo'] == 'Derrota'])
    
    prob_victoria = round((victorias / total_matches) * 100, 1)
    
    # Probabilidad de Ambos Anotan (BTTS)
    btts_count = len(df_t[(df_t['goles_favor'] > 0) & (df_t['goles_contra'] > 0)])
    prob_btts = round((btts_count / total_matches) * 100, 1)
    
    # PROMEDIOS GENERALES (Todos los que registras en tus partidos)
    prom_gf = round(df_t['goles_favor'].mean(), 2)
    prom_gc = round(df_t['goles_contra'].mean(), 2)
    prom_gf1t = round(df_t['goles_favor_1t'].mean(), 2)
    prom_gf2t = round(df_t['goles_favor_2t'].mean(), 2)
    prom_tt = round(df_t['tiros_totales'].mean(), 2)
    prom_tap = round(df_t['tiros_a_puerta'].mean(), 2)
    prom_tpalo = round(df_t['tiros_al_palo'].mean(), 2) if 'tiros_al_palo' in df_t.columns else 0.0
    prom_corners = round(df_t['corners'].mean(), 2)
    prom_atajadas = round(df_t['atajadas'].mean(), 2) if 'atajadas' in df_t.columns else 0.0
    prom_amarillas = round(df_t['tarjetas_amarillas'].mean(), 2)
    prom_rojas = round(df_t['tarjetas_rojas'].mean(), 2) if 'tarjetas_rojas' in df_t.columns else 0.0
    prom_faltas = round(df_t['faltas_cometidas'].mean(), 2)
    prom_offsides = round(df_t['fueras_de_juego'].mean(), 2) if 'fueras_de_juego' in df_t.columns else 0.0
    
    st.write("")
    st.markdown("---")
    st.markdown(f"<h3>🎯 Indicadores Analíticos Principales para: <b>{equipo_sel}</b></h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #888;'>Basado en una muestra de <b>{total_matches} partidos</b> registrados (Victorias: {victorias} | Empates: {empates} | Derrotas: {derrotas}).</p>", unsafe_allow_html=True)
    
    # Porcentajes generales de gol por tiempo (al menos 1 gol)
    goles_1t_almenos_1 = len(df_t[df_t['goles_favor_1t'] > 0])
    goles_2t_almenos_1 = len(df_t[df_t['goles_favor_2t'] > 0])
    prob_1t_gral = round((goles_1t_almenos_1 / total_matches) * 100, 1)
    prob_2t_gral = round((goles_2t_almenos_1 / total_matches) * 100, 1)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="🏆 % Probabilidad Victoria", value=f"{prob_victoria}%", delta=f"{victorias} Victorias")
    with c2:
        st.metric(label="⏱️ % Anota en 1er Tiempo", value=f"{prob_1t_gral}%", delta=f"{goles_1t_almenos_1} partidos")
    with c3:
        st.metric(label="⏱️ % Anota en 2do Tiempo", value=f"{prob_2t_gral}%", delta=f"{goles_2t_almenos_1} partidos")
    with c4:
        st.metric(label="⚽ Probabilidad BTTS", value=f"{prob_btts}%", delta=f"{btts_count} partidos")

    st.write("")
    st.markdown("---")
    st.markdown("<h4>📈 Simulador OVER de Goles por Tiempo Específico</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0;'>Calcula la probabilidad histórica de que el equipo anote <b>MÁS DE</b> una cantidad de goles en el tiempo seleccionado.</p>", unsafe_allow_html=True)
    
    col_over1, col_over2, col_over3 = st.columns(3)
    with col_over1:
        tiempo_over = st.selectbox("Selecciona el Tiempo (Over):", options=["Primer Tiempo (1T)", "Segundo Tiempo (2T)"], key="sel_t_over")
    with col_over2:
        linea_over = st.selectbox("Línea Over (Más de):", options=[0.5, 1.5, 2.5, 3.5], index=0, key="sel_linea_over")
    with col_over3:
        st.write("")
        st.write("")
        
    columna_db_over = 'goles_favor_1t' if "1T" in tiempo_over else 'goles_favor_2t'
    partidos_cumplen_over = len(df_t[df_t[columna_db_over] > linea_over])
    prob_over_tiempo = round((partidos_cumplen_over / total_matches) * 100, 1)
    
    st.metric(
        label=f"🔥 Probabilidad OVER +{linea_over} goles en el {tiempo_over.split()[0]}",
        value=f"{prob_over_tiempo}%",
        delta=f"{partidos_cumplen_over} de {total_matches} partidos"
    )

    st.write("")
    st.markdown("---")
    st.markdown("<h4>📉 Simulador UNDER de Goles por Tiempo Específico</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0;'>Calcula la probabilidad histórica de que el equipo anote <b>MENOS DE</b> una cantidad de goles en el tiempo seleccionado.</p>", unsafe_allow_html=True)
    
    col_under1, col_under2, col_under3 = st.columns(3)
    with col_under1:
        tiempo_under = st.selectbox("Selecciona el Tiempo (Under):", options=["Primer Tiempo (1T)", "Segundo Tiempo (2T)"], key="sel_t_under")
    with col_under2:
        linea_under = st.selectbox("Línea Under (Menos de):", options=[0.5, 1.5, 2.5, 3.5], index=1, key="sel_linea_under")
    with col_under3:
        st.write("")
        st.write("")
        
    columna_db_under = 'goles_favor_1t' if "1T" in tiempo_under else 'goles_favor_2t'
    partidos_cumplen_under = len(df_t[df_t[columna_db_under] < linea_under])
    prob_under_tiempo = round((partidos_cumplen_under / total_matches) * 100, 1)
    
    st.metric(
        label=f"❄️ Probabilidad UNDER -{linea_under} goles en el {tiempo_under.split()[0]}",
        value=f"{prob_under_tiempo}%",
        delta=f"{partidos_cumplen_under} de {total_matches} partidos"
    )

    st.write("")
    st.markdown("---")
    st.markdown("<h4>📊 Promedios Generales por Partido (Estadísticas Completas)</h4>", unsafe_allow_html=True)
    
    # Fila 1 de Promedios
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric(label="⚽ Goles a Favor", value=prom_gf)
    with m2:
        st.metric(label="⏱️ Goles Favor (1T)", value=prom_gf1t)
    with m3:
        st.metric(label="⏱️ Goles Favor (2T)", value=prom_gf2t)
    with m4:
        st.metric(label="🛡️ Goles en Contra", value=prom_gc)
    with m5:
        st.metric(label="🎯 Tiros Totales", value=prom_tt)
    with m6:
        st.metric(label="🥅 Tiros a Puerta", value=prom_tap)

    # Fila 2 de Promedios
    m7, m8, m9, m10, m11, m12, m13 = st.columns(7)
    with m7:
        st.metric(label="🪵 Tiros al Palo", value=prom_tpalo)
    with m8:
        st.metric(label="🚩 Córners", value=prom_corners)
    with m9:
        st.metric(label="🧤 Atajadas", value=prom_atajadas)
    with m10:
        st.metric(label="🟨 T. Amarillas", value=prom_amarillas)
    with m11:
        st.metric(label="🟥 T. Rojas", value=prom_rojas)
    with m12:
        st.metric(label="⚠️ Faltas Cometidas", value=prom_faltas)
    with m13:
        st.metric(label="🚩 Fueras de Juego", value=prom_offsides)

    st.write("")
    st.markdown("---")
    st.markdown("<h4>🎛️ Simulador de Líneas Over / Under (Goles Totales del Partido)</h4>", unsafe_allow_html=True)
    
    df_t['goles_totales_partido'] = df_t['goles_favor'] + df_t['goles_contra']
    lineas_disponibles = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
    linea_seleccionada = st.selectbox("Selecciona la línea de Goles Totales (Partido Completo):", options=lineas_disponibles, index=2)
    
    partidos_over_total = len(df_t[df_t['goles_totales_partido'] > linea_seleccionada])
    partidos_under_total = len(df_t[df_t['goles_totales_partido'] < linea_seleccionada])
    
    prob_over_total = round((partidos_over_total / total_matches) * 100, 1)
    prob_under_total = round((partidos_under_total / total_matches) * 100, 1)
    
    s1, s2 = st.columns(2)
    with s1:
        st.metric(label=f"📈 Probabilidad OVER +{linea_seleccionada} Goles (Global)", value=f"{prob_over_total}%", delta=f"{partidos_over_total} partidos")
    with s2:
        st.metric(label=f"📉 Probabilidad UNDER -{linea_seleccionada} Goles (Global)", value=f"{prob_under_total}%", delta=f"{partidos_under_total} partidos")

# ==============================================================================
# ENRUTADOR PRINCIPAL DE VISTAS (ROUTER)
# ==============================================================================
if st.session_state['pagina'] == 'inicio':
    inicio()
elif st.session_state['pagina'] == 'formulario_equipos':
    formulario_equipos()
elif st.session_state['pagina'] == 'visualizador':
    visualizador_base_datos()
elif st.session_state['pagina'] == 'comparar_equipos':
    comparar_equipos()
elif st.session_state['pagina'] == 'calculadora':
    calculadora_probabilidades()

# ==============================================================================
# PIE DE PÁGINA (FOOTER)
# ==============================================================================
st.markdown("""
    <div class="footer">
        Desarrollado con <span>Streamlit</span> y <span>Supabase</span> | Sistema de Apuestas Deportivas <span>YANESBET</span> ⚽
    </div>
""", unsafe_allow_html=True)
