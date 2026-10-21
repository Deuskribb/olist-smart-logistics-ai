import streamlit as st
import pandas as pd
import plotly.express as px
import pulp

# Configuración de página
st.set_page_config(page_title="Optimización Logística Olist", layout="wide")

st.title("🚚 Dashboard de Optimización Logística y Flota")
st.markdown("Predicción de demanda de carga mediante **XGBoost** y asignación óptima de camiones con **PuLP**.")

# --- BARRA LATERAL (Controles interactivos) ---
st.sidebar.header("Parámetros de Simulación")
prediccion_volumen = st.sidebar.slider("Volumen Predicho (kg/vol)", 50000, 1000000, 532718, step=10000)
mae_modelo = st.sidebar.number_input("Error del Modelo (MAE)", value=150.5)
factor_estiba = st.sidebar.slider("Factor de Estiba", 0.50, 1.00, 0.85)

# --- LÓGICA DE OPTIMIZACIÓN ---
volumen_necesario = (prediccion_volumen + mae_modelo) / factor_estiba

problema = pulp.LpProblem("Optimizar_Flota", pulp.LpMinimize)
c_pequeño = pulp.LpVariable("Pequeño", lowBound=0, cat='Integer')
c_mediano = pulp.LpVariable("Mediano", lowBound=0, cat='Integer')
c_grande = pulp.LpVariable("Grande", lowBound=0, cat='Integer')

problema += 350*c_pequeño + 900*c_mediano + 1800*c_grande, "Costo_Total"
problema += 1500*c_pequeño + 6000*c_mediano + 14000*c_grande >= volumen_necesario

problema.solve(pulp.PULP_CBC_CMD(msg=False))

costo_total = pulp.value(problema.objective)
cant_p = int(c_pequeño.varValue)
cant_m = int(c_mediano.varValue)
cant_g = int(c_grande.varValue)

# --- TARJETAS KPI ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Volumen Requerido", f"{volumen_necesario:,.0f} kg")
col2.metric("Costo Total Mínimo", f"R$ {costo_total:,.2f}")
col3.metric("Camiones Grandes", f"{cant_g} unidades")
col4.metric("Flota Total", f"{cant_p + cant_m + cant_g} vehículos")

st.divider()

# --- GRÁFICOS Y RESULTADOS ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Distribución de la Flota Recomendada")
    df_flota = pd.DataFrame({
        "Tipo": ["Pequeño (1.5t)", "Mediano (6t)", "Grande (14t)"],
        "Cantidad": [cant_p, cant_m, cant_g]
    })
    fig = px.bar(df_flota, x="Tipo", y="Cantidad", color="Tipo", text_auto=True,
                 title="Camiones a Contratar")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Eficiencia de Capacidad")
    capacidad_contratada = (cant_p * 1500) + (cant_m * 6000) + (cant_g * 14000)
    holgura = capacidad_contratada - volumen_necesario
    
    st.write(f"**Capacidad Total Contratada:** {capacidad_contratada:,.0f} kg")
    st.write(f"**Margen de Seguridad Libre:** {holgura:,.2f} kg")
    st.progress(min(volumen_necesario / capacidad_contratada, 1.0))