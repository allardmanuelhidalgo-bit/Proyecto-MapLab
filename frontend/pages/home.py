# frontend/pages/home.py
#
# Vista Home de MapLab (antes vivía en app.py).
#
# Objetivo de esta vista (por ahora):
# - Confirmar que el frontend levanta correctamente.
# - Mostrar el header de la app.
# - Mostrar el mapa con las tiendas registradas (o datos de ejemplo si el
#   backend/base de datos todavía no están listos).

import streamlit as st
from utils import obtener_tiendas, backend_esta_disponible
from elements.header import render_header

st.set_page_config(
    page_title="MapLab - Comparador de precios",
    page_icon="🗺️",
    layout="wide",
)

# ---------------------------------------------------------------------
# HEADER (componente compartido - ver frontend/elements/header.py)
# ---------------------------------------------------------------------
busqueda = render_header()

# ---------------------------------------------------------------------
# AVISO DE ESTADO DEL BACKEND (solo mientras se sigue desarrollando)
# ---------------------------------------------------------------------
if not backend_esta_disponible():
    st.warning(
        "No se pudo conectar con el backend (¿está corriendo `uvicorn "
        "backend.main:app --reload`?). Mostrando datos de ejemplo mientras tanto."
    )

# ---------------------------------------------------------------------
# CONTENIDO PRINCIPAL: MAPA
# ---------------------------------------------------------------------
st.subheader("Tiendas registradas")

tiendas = obtener_tiendas()

col_mapa, col_lista = st.columns([2, 1])

with col_mapa:
    st.map(tiendas, latitude="lat", longitude="lon", size=60)

with col_lista:
    st.write("**Tiendas en el mapa:**")
    for _, tienda in tiendas.iterrows():
        st.markdown(f"📍 **{tienda['nombre']}**  \n{tienda['direccion']}")

st.success("Home cargado correctamente ✅ — esta es la vista provisional del mapa.")