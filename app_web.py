import streamlit as st
import pandas as pd

# Configuración de la página para dispositivos móviles
st.set_page_config(page_title="Dashboard de Apuestas", layout="centered")

st.title("⚽ Predicciones y Estadísticas")
st.subheader("Consulta rápida de promedios para tus apuestas.")

# --- CONEXIÓN A LA BASE DE DATOS SUPABASE ---
conn = st.connection("supabase", type="sql")

# Consulta principal para obtener todas las estadísticas desde Supabase
try:
    query = "SELECT * FROM estadisticas_equipos"
    df = conn.query(query, ttl=0)
except Exception as e:
    st.error(f"Error al leer los datos: {e}")
    df = pd.DataFrame()

if not df.empty:
    # Selector de equipo adaptado para móvil
    equipos_disponibles = df['equipo_analizado'].unique()
    equipo_seleccionado = st.selectbox("Selecciona un equipo:", equipos_disponibles)
    
    # Filtrar datos del equipo seleccionado
    df_equipo = df[df['equipo_analizado'] == equipo_seleccionado]
    
    st.subheader(f"📊 Estadísticas de {equipo_seleccionado}")
    
    # Tabla con todos los detalles incluyendo las nuevas métricas
    columnas_mostrar = [
        'fecha_partido', 'rival', 'competicion', 'resultado_equipo', 
        'goles_favor', 'goles_contra', 'atajadas', 'tarjetas', 'faltas', 'corners'
    ]
    # Filtramos solo las columnas que existan realmente en el DataFrame para evitar errores
    columnas_validas = [col for col in columnas_mostrar if col in df_equipo.columns]
    st.dataframe(df_equipo[columnas_validas])
    
    st.markdown("### 📈 Promedios por Partido")
    
    # Cálculo automático de promedios para apuestas
    prom_gf = df_equipo['goles_favor'].mean() if 'goles_favor' in df_equipo else 0
    prom_gc = df_equipo['goles_contra'].mean() if 'goles_contra' in df_equipo else 0
    prom_corners = df_equipo['corners'].mean() if 'corners' in df_equipo else 0
    prom_tarjetas = df_equipo['tarjetas'].mean() if 'tarjetas' in df_equipo else 0
    prom_faltas = df_equipo['faltas'].mean() if 'faltas' in df_equipo else 0
    prom_atajadas = df_equipo['atajadas'].mean() if 'atajadas' in df_equipo else 0

    # Organización de métricas en filas adaptadas para pantalla móvil
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Prom. Goles Favor", value=round(prom_gf, 2))
        st.metric(label="Prom. Córners", value=round(prom_corners, 2))
        st.metric(label="Prom. Faltas", value=round(prom_faltas, 2))
    with col2:
        st.metric(label="Prom. Goles Contra", value=round(prom_gc, 2))
        st.metric(label="Prom. Tarjetas", value=round(prom_tarjetas, 2))
        st.metric(label="Prom. Atajadas", value=round(prom_atajadas, 2))
else:
    st.info("Aún no hay registros en la base de datos o se está estableciendo la conexión.")
