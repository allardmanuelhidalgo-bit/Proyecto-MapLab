# frontend/pages/comparar_precios.py
#
# Página de EJEMPLO para mostrar cómo se reutiliza el header en otra
# vista. Streamlit detecta automáticamente cualquier archivo .py
# dentro de frontend/pages/ y lo agrega como una vista nueva (con su
# propio menú en la barra lateral), sin que haya que registrarla en
# ningún lado.

import streamlit as st
from elements.header import render_header

st.set_page_config(
    page_title="MapLab - Comparar precios",
    page_icon="🗺️",
    layout="wide",
)

# Mismo header que en home.py, convocado desde elements/header.py
busqueda = render_header()

st.subheader("Comparar precios")
st.write(
    "Esta es una página de ejemplo para mostrar que el header se "
    "reutiliza igual en cualquier rama de la app."
)

if busqueda:
    st.info(f"Buscando: **{busqueda}** (todavía sin conectar a resultados reales)")