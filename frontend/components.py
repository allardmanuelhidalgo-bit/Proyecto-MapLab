# frontend/pages/1_Comparar_Precios.py
#
# Página de EJEMPLO para mostrar cómo se reutiliza el header en otra
# "rama" de la app. Streamlit detecta automáticamente cualquier
# archivo .py dentro de frontend/pages/ y lo agrega como una página
# nueva (con su propio menú en la barra lateral), sin que haya que
# registrarla en ningún lado.
#
# El número al inicio del nombre del archivo ("1_") solo define el
# orden en el menú lateral; no afecta el código.

import streamlit as st
from elements.header import render_header

st.set_page_config(
    page_title="MapLab - Comparar precios",
    page_icon="🗺️",
    layout="wide",
)

# Mismo header que en app.py, convocado desde components.py
busqueda = render_header()

st.subheader("Comparar precios")
st.write(
    "Esta es una página de ejemplo para mostrar que el header se "
    "reutiliza igual en cualquier rama de la app."
)

if busqueda:
    st.info(f"Buscando: **{busqueda}** (todavía sin conectar a resultados reales)")