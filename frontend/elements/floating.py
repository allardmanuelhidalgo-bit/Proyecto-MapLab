# frontend/elements/floating.py
#
# Helper para dibujar "paneles flotantes" sobre el mapa, al estilo
# Google Maps (buscador arriba, botones de acción abajo, etc.).
#
# Cómo funciona:
# - Desde Streamlit 1.37, st.container(key="algo") le agrega la clase
#   CSS "st-key-algo" al div que lo envuelve.
# - Envolvemos el mapa + los paneles en un container con key fijo
#   (MAPA_WRAPPER_KEY) y lo ponemos position:relative.
# - Cada panel es OTRO container con su propio key, puesto
#   position:absolute con la esquina que le indiques. Como todos
#   cuelgan del mismo wrapper "relative", flotan sobre el mapa sin
#   importar el orden en que Streamlit los renderiza.

import streamlit as st

MAPA_WRAPPER_KEY = "mapa_area"

# posición -> CSS (top/left/right/bottom)
_POSICIONES = {
    "top-left": "top: 16px; left: 16px;",
    "top-right": "top: 16px; right: 16px;",
    "bottom-left": "bottom: 16px; left: 16px;",
    "bottom-right": "bottom: 16px; right: 16px;",
    "top-center": "top: 16px; left: 50%; transform: translateX(-50%);",
}


def inyectar_estilos_flotantes(paneles: dict[str, str], alto_mapa_px: int = 600):
    """
    paneles: {"nombre_del_panel_key": "top-left" | "top-right" | "bottom-left" | "bottom-right" | "top-center"}
    Llamar UNA vez por página, antes de dibujar el wrapper y los paneles.
    """
    reglas_paneles = "\n".join(
        f"""
        div.st-key-{key} {{
            position: absolute;
            {_POSICIONES[pos]}
            z-index: 999;
            background: white;
            border-radius: 12px;
            padding: 0.6rem 0.8rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.18);
            max-width: 340px;
            max-height: 75%;
            overflow-y: auto;
        }}
        """
        for key, pos in paneles.items()
    )

    st.markdown(
        f"""
        <style>
        div.st-key-{MAPA_WRAPPER_KEY} {{
            position: relative;
            height: {alto_mapa_px}px;
        }}
        div.st-key-{MAPA_WRAPPER_KEY} iframe {{
            border-radius: 12px;
        }}
        {reglas_paneles}
        </style>
        """,
        unsafe_allow_html=True,
    )