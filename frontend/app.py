# frontend/app.py
#
# Home provisional de MapLab.
#
# Objetivo de esta vista (por ahora):
# - Confirmar que el frontend levanta correctamente.
# - Mostrar un header propio de la app.
# - Mostrar el mapa con las tiendas registradas (o datos de ejemplo si el
#   backend/base de datos todavía no están listos).
#
# Cuando el resto de pantallas (búsqueda de producto, comparación de
# precios, etc.) estén listas, esta vista se puede ir reemplazando o
# convirtiendo en la página de bienvenida dentro de una navegación con
# varias páginas.
#
# NOTA: este archivo NO debe tener un docstring de módulo (""" ... """)
# antes de st.set_page_config(). Streamlit trata cualquier string suelto
# como un "magic command" (lo imprime en pantalla como si fuera
# st.write(...)), y eso cuenta como un comando ejecutado ANTES que
# set_page_config(), lo cual Streamlit no permite (debe ser el primero).

import streamlit as st
from utils import obtener_tiendas, backend_esta_disponible

st.set_page_config(
    page_title="MapLab - Comparador de precios",
    page_icon="🗺️",
    layout="wide",
)

# ---------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
        .maplab-header {
            background-color: #1E3A5F;
            padding: 1.2rem 2rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
        }
        .maplab-header h1 {
            color: #FFFFFF;
            margin: 0;
            font-size: 2rem;
        }
        .maplab-header p {
            color: #CFE0F0;
            margin: 0.2rem 0 0 0;
            font-size: 1rem;
        }
    </style>

    <div class="maplab-header">
        <h1>🗺️ MapLab</h1>
        <p>Encuentra el mejor precio cerca de ti, actualizado por la comunidad</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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