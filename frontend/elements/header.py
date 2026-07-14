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
from utils import usuario_actual, identificarse, cerrar_sesion


def _render_identificacion():
    """Pequeño panel para crear/mostrar el usuario actual (sin contraseña).
    Varios endpoints del backend (votar, reportar precio, lista personal)
    necesitan un usuario_id, así que esto vive en el header para estar
    disponible en cualquier página."""
    usuario = usuario_actual()

    if usuario:
        with st.popover(f"👤 {usuario['nombre']}", use_container_width=True):
            st.caption(usuario["email"])
            if st.button("Cerrar sesión", key="btn_cerrar_sesion"):
                cerrar_sesion()
                st.rerun()
    else:
        with st.popover("👤 Identificarme", use_container_width=True):
            st.caption("Necesario para votar, reportar precios o tener una lista personal.")
            nombre = st.text_input("Nombre", key="id_nombre")
            email = st.text_input("Email", key="id_email")
            if st.button("Continuar", key="btn_identificarse"):
                if not nombre or not email:
                    st.warning("Completa nombre y email.")
                else:
                    ok, msg = identificarse(nombre, email)
                    if ok:
                        st.rerun()
                    else:
                        st.error(msg)


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
        col_home, col_buscador, col_logo, col_usuario = st.columns([0.08, 0.5, 0.20, 0.22])

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

        with col_usuario:
            _render_identificacion()

        st.markdown("</div>", unsafe_allow_html=True)

    st.session_state["busqueda"] = busqueda
    return busqueda