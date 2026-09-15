import streamlit as st
import pandas as pd

def mostrar_calculadora_avanzada():
    # Título principal de la sección en la aplicación
    st.title("📊 Calculadora Avanzada de Mercados y Probabilidades")
    st.markdown("Analiza el rendimiento histórico de los equipos combinando líneas de **Over/Under** con filtros de **Local y Visitante**.")

    # 1. Establecer la conexión con Supabase utilizando el conector nativo de Streamlit
    conn = st.connection("supabase", type="sql")

    # 2. Consultar la lista de equipos únicos disponibles en la base de datos para el selector
    query_equipos = "SELECT DISTINCT equipo_analizado FROM estadisticas_equipos ORDER BY equipo_analizado;"
    df_equipos = conn.query(query_equipos, ttl=0)

    # Validar si la tabla tiene datos para evitar errores visuales
    if df_equipos.empty:
        st.warning("⚠️ No hay equipos registrados en la base de datos de Supabase. Agrega registros primero.")
        return

    # 3. Crear los controles principales en la interfaz (Filtros Globales)
    col1, col2 = st.columns(2)
    
    with col1:
        # Selector desplegable con los nombres de los equipos
        equipo_elegido = st.selectbox("Selecciona el Equipo a Analizar:", df_equipos['equipo_analizado'].tolist())

    with col2:
        # Selector de condición para filtrar localía
        condicion_elegida = st.selectbox("Condición del Partido:", ["Todos", "Local", "Visitante"])

    st.divider()
    st.subheader(f"📈 Análisis Estadístico para: {equipo_elegido} ({condicion_elegida})")

    # 4. Construir la consulta SQL dinámica basada en la condición seleccionada
    if condicion_elegida == "Local":
        query_datos = f"""
            SELECT * FROM estadisticas_equipos 
            WHERE equipo_analizado = '{equipo_elegido}' AND condicion = 'Local';
        """
    elif condicion_elegida == "Visitante":
        query_datos = f"""
            SELECT * FROM estadisticas_equipos 
            WHERE equipo_analizado = '{equipo_elegido}' AND condicion = 'Visitante';
        """
    else:
        query_datos = f"""
            SELECT * FROM estadisticas_equipos 
            WHERE equipo_analizado = '{equipo_elegido}';
        """

    # Ejecutar la consulta para traer todo el histórico de ese filtro
    df_stats = conn.query(query_datos, ttl=0)

    # Validar si el equipo tiene partidos bajo ese filtro específico
    if df_stats.empty:
        st.info(f"ℹ️ El equipo {equipo_elegido} no registra partidos bajo la condición '{condicion_elegida}'.")
        return

    # Mostrar el total de muestras (partidos analizados)
    total_partidos = len(df_stats)
    st.caption(f"Muestra analizada: **{total_partidos} partidos** encontrados en Supabase.")

    # 5. Organizar las métricas en Pestañas (Tabs) visuales para limpiar la interfaz
    tab_corners, tab_tiros, tab_disciplina, tab_goles = st.tabs([
        "🚩 Córners y Tiros", 
        "🎯 Remates al Arco", 
        "🟨 Tarjetas y Faltas", 
        "⚽ Goles y Mitades"
    ])

    # --- PESTAÑA 1: CÓRNERS ---
    with tab_corners:
        st.markdown("### Mercado de Córners")
        # Selector interactivo de línea Over/Under para córners
        linea_corners = st.slider("Selecciona la línea de Córners:", min_value=0.5, max_value=12.5, value=4.5, step=1.0, key="slider_corners")
        
        # Calcular porcentajes matemáticos
        partidos_over_c = len(df_stats[df_stats['corners'] > linea_corners])
        pct_over_c = (partidos_over_c / total_partidos) * 100
        pct_under_c = 100 - pct_over_c
        media_c = df_stats['corners'].mean()

        # Renderizar tarjetas visuales de métricas
        c1, c2, c3 = st.columns(3)
        c1.metric(label=f"Over {linea_corners} Córners", value=f"{pct_over_c:.1f}%", help="Porcentaje de partidos donde superó esta línea")
        c2.metric(label=f"Under {linea_corners} Córners", value=f"{pct_under_c:.1f}%", help="Porcentaje de partidos por debajo de esta línea")
        c3.metric(label="Promedio de Córners", value=f"{media_c:.2f}")

    # --- PESTAÑA 2: REMATES AL ARCO ---
    with tab_tiros:
        st.markdown("### Mercado de Tiros a Puerta")
        linea_tiros = st.slider("Selecciona la línea de Tiros a Puerta:", min_value=0.5, max_value=10.5, value=3.5, step=1.0, key="slider_tiros")
        
        partidos_over_t = len(df_stats[df_stats['tiros_a_puerta'] > linea_tiros])
        pct_over_t = (partidos_over_t / total_partidos) * 100
        pct_under_t = 100 - pct_over_t
        media_t = df_stats['tiros_a_puerta'].mean()

        t1, t2, t3 = st.columns(3)
        t1.metric(label=f"Over {linea_tiros} Tiros a Puerta", value=f"{pct_over_t:.1f}%")
        t2.metric(label=f"Under {linea_tiros} Tiros a Puerta", value=f"{pct_under_t:.1f}%")
        t3.metric(label="Promedio Tiros a Puerta", value=f"{media_t:.2f}")

    # --- PESTAÑA 3: TARJETAS Y FALTAS ---
    with tab_disciplina:
        st.markdown("### Mercado de Disciplina (Tarjetas Amarillas)")
        linea_tarjetas = st.slider("Selecciona la línea de Tarjetas Amarillas:", min_value=0.5, max_value=6.5, value=1.5, step=1.0, key="slider_tarjetas")
        
        partidos_over_tar = len(df_stats[df_stats['tarjetas_amarillas'] > linea_tarjetas])
        pct_over_tar = (partidos_over_tar / total_partidos) * 100
        pct_under_tar = 100 - pct_over_tar
        media_tar = df_stats['tarjetas_amarillas'].mean()

        d1, d2, d3 = st.columns(3)
        d1.metric(label=f"Over {linea_tarjetas} Amarillas", value=f"{pct_over_tar:.1f}%")
        d2.metric(label=f"Under {linea_tarjetas} Amarillas", value=f"{pct_under_tar:.1f}%")
        d3.metric(label="Promedio Tarjetas Amarillas", value=f"{media_tar:.2f}")

    # --- PESTAÑA 4: GOLES Y MITADES ---
    with tab_goles:
        st.markdown("### Mercado de Goles (A Favor / En Contra)")
        linea_goles = st.slider("Selecciona la línea de Goles Totales del Equipo:", min_value=0.5, max_value=4.5, value=1.5, step=1.0, key="slider_goles")
        
        partidos_over_g = len(df_stats[df_stats['goles_favor'] > linea_goles])
        pct_over_g = (partidos_over_g / total_partidos) * 100
        pct_under_g = 100 - pct_over_g
        media_g = golongan = df_stats['goles_favor'].mean()

        g1, g2, g3 = st.columns(3)
        g1.metric(label=f"Over {linea_goles} Goles", value=f"{pct_over_g:.1f}%")
        g2.metric(label=f"Under {linea_goles} Goles", value=f"{pct_under_g:.1f}%")
        g3.metric(label="Promedio Goles a Favor", value=f"{media_g:.2f}")

# Llamar a la función principal si se ejecuta el script
if __name__ == "__main__":
    mostrar_calculadora_avanzada()