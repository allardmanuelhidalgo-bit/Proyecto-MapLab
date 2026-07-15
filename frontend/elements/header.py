# frontend/elements/header.py
#
# Header de MapLab (versión de una sola vista, sin login):
# solo logo + buscador. El buscador es lo único que dispara el panel
# flotante de comparación de precios en app.py.

import streamlit as st


def render_header():
    """
    Dibuja el header de MapLab: logo + buscador de productos.

    Devuelve
    --------
    str
        El texto que el usuario haya escrito en el buscador (puede
        estar vacío). También queda guardado en
        st.session_state["busqueda"] para que el resto de la app lo
        pueda leer sin tener que pasarse el valor entre funciones.
    """

    st.markdown(
        """
        <style>
            .maplab-header-bar {
                background-color: #1E3A5F;
                padding: 0.8rem 1.5rem;
                border-radius: 10px;
                margin-bottom: 1.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="maplab-header-bar">', unsafe_allow_html=True)
        col_logo, col_buscador = st.columns([0.25, 0.75])

        with col_logo:
            st.markdown(
                "<h3 style='color:white; margin:0;'>🗺️ MapLab</h3>",
                unsafe_allow_html=True,
            )

        with col_buscador:
            busqueda = st.text_input(
                "Buscar",
                placeholder="Buscar producto (ej: leche, arroz, detergente...)",
                label_visibility="collapsed",
                key="header_busqueda",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.session_state["busqueda"] = busqueda
    return busqueda