import streamlit as st
import pandas as pd
from sqlalchemy import text

# Configuración de la página para que no se vea mal en el celular
st.set_page_config(page_title="Dashboard de Apuestas", layout="centered")

st.title("⚽ Predicciones y Estadísticas")
st.subheader("Consulta rápida de promedios para tus apuestas.")

# --- CONEXIÓN A LA BASE DE DATOS SUPABASE ---
conn = st.connection("supabase", type="sql")

# Consulta principal para obtener las estadísticas desde Supabase
try:
    query = "SELECT * FROM estadisticas_equipos"
    df = conn.query(query, ttl=0)
except Exception as e:
    st.error(f"Error al leer los datos: {e}")
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
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Promedio Goles a Favor", value=round(prom_gf, 2))
    with col2:
        st.metric(label="Promedio Goles en Contra", value=round(prom_gc, 2))
else:
    st.info("Aún no hay registros en la base de datos o se está estableciendo la conexión.")
