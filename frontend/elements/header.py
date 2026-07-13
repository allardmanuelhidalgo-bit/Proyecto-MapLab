# frontend/elements/header.py
#
# Header reutilizable de MapLab.
#
# La idea es que cada página (app.py y todo lo que pongas dentro de
# frontend/pages/) haga:
#     from elements.header import render_header
# y lo llame al inicio, en vez de repetir el HTML/CSS del header en
# cada archivo.

import streamlit as st


def render_header(pagina_home: str = "pages/home.py"):
    """
    Dibuja el header de MapLab: logo, botón cuadrado para volver al
    home, y un buscador de productos/tiendas.

    Parámetros
    ----------
    pagina_home : str
        Ruta del archivo que representa el "Home" de la app, tal como
        Streamlit lo espera en st.switch_page(). Por defecto apunta a
        "pages/home.py", que es donde vive la vista Home. Si algún día
        mueven ese archivo, solo hay que actualizar este valor.

    Devuelve
    --------
    str
        El texto que el usuario haya escrito en el buscador (puede
        estar vacío). También queda guardado en
        st.session_state["busqueda"] para que cualquier página lo pueda
        leer sin tener que pasarse el valor entre archivos.
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
            div[data-testid="stHorizontalBlock"] .stButton button {
                background-color: #FFFFFF;
                border: none;
                font-size: 1.1rem;
                padding: 0.35rem 0.7rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="maplab-header-bar">', unsafe_allow_html=True)
        col_home, col_buscador, col_logo = st.columns([0.08, 0.62, 0.30])

        with col_home:
            # Botón cuadrado -> regresa al home.
            # Cambia el emoji si más adelante quieren un ícono distinto
            # (por ejemplo "🏠"), la lógica de navegación no cambia.
            if st.button("⬜", key="btn_home", help="Ir al inicio"):
                st.switch_page(pagina_home)

        with col_buscador:
            busqueda = st.text_input(
                "Buscar",
                placeholder="Buscar producto o tienda...",
                label_visibility="collapsed",
                key="header_busqueda",
            )

        with col_logo:
            st.markdown(
                "<h3 style='color:white; margin:0;'>🗺️ MapLab</h3>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.session_state["busqueda"] = busqueda
    return busqueda