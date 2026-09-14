import streamlit as st
import mysql.connector
import pandas as pd

# Configuración de la página para que se vea bien en el celular
st.set_page_config(page_title="Dashboard de Apuestas", layout="centered")

st.title("⚽ Predicciones y Estadísticas")
st.markdown("Consulta rápida de promedios para tus apuestas.")

# Conexión a la base de datos protegida con try-except
@st.cache_resource
def conectar_db():
    try:
        return mysql.connector.connect(
            host="tu_servidor_remoto.com",
            user="tu_usuario",
            password="tu_password",
            database="apuestasdeportivas",
            connection_timeout=5
        )
    except Exception:
        return None

conexion = conectar_db()

if conexion and conexion.is_connected():
    try:
        query = "SELECT * FROM estadisticas_equipos"
        df = pd.read_sql(query, conexion)
    except Exception as e:
        st.error(f"Error al leer los datos: {e}")
        df = pd.DataFrame()
else:
    df = pd.DataFrame()

if not df.empty:
    # Selector de equipo desde el celular
    equipos_disponibles = df['equipo_analizado'].unique()
    equipo_seleccionado = st.selectbox("Selecciona un equipo:", equipos_disponibles)

    # Filtrar datos del equipo
    df_equipo = df[df['equipo_analizado'] == equipo_seleccionado]

    st.subheader(f"📊 Estadísticas de {equipo_seleccionado}")
    st.dataframe(df_equipo[['fecha_partido', 'rival', 'competicion', 'resultado_equipo', 'goles_favor', 'goles_contra']])

    # Cálculo automático de promedios y probabilidades básicas
    prom_gf = df_equipo['goles_favor'].mean()
    prom_gc = df_equipo['goles_contra'].mean()
    prom_tiros = df_equipo['tiros_totales'].mean()
    prom_corners = df_equipo['corners'].mean()

    st.markdown("### 📈 Promedios Clave")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Goles a Favor (Promedio)", round(prom_gf, 2))
        st.metric("Tiros Totales (Promedio)", round(prom_tiros, 2))
    with col2:
        st.metric("Goles en Contra (Promedio)", round(prom_gc, 2))
        st.metric("Córneres (Promedio)", round(prom_corners, 2))

    # Sección de probabilidades orientadas a apuestas
    st.markdown("### 🎲 Estimaciones para el próximo partido")
    prob_over_15 = (df_equipo['goles_favor'] + df_equipo['goles_contra'] > 1.5).mean() * 100
    st.info((f"Probabilidad estimada de +1.5 goles en sus partidos: **{round(prob_over_15, 1)}%**"))
else:
    st.warning("⚠️ No hay una conexión activa a la base de datos remota en este momento. La interfaz está en línea correctamente.")
