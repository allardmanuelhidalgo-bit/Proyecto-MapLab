# frontend/app.py
#
# Este archivo ya no dibuja nada por sí mismo. Streamlit siempre
# necesita un archivo de entrada (el que se corre con
# "streamlit run frontend/app.py"), pero toda la vista real ahora
# vive en pages/home.py. Aquí solo redirigimos para que abrir la app
# te lleve directo a home.

import streamlit as st

st.switch_page("pages/home.py")