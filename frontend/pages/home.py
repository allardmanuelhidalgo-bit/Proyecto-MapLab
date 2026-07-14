# frontend/pages/home.py
#
# Vista Home de MapLab:
# - Pide la ubicación real del usuario (geolocalización del navegador).
# - Muestra un mapa (folium) con paneles flotantes estilo Google Maps.
# - Al hacer click en una tienda del mapa, aparece un panel flotante
#   con la opción de iniciar una ruta hacia ella.

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from utils import obtener_tiendas, backend_esta_disponible, obtener_ubicacion_usuario, ubicacion_es_real
from elements.header import render_header
from elements.floating import inyectar_estilos_flotantes, MAPA_WRAPPER_KEY

st.set_page_config(
    page_title="MapLab - Comparador de precios",
    page_icon="🗺️",
    layout="wide",
)

busqueda = render_header()

if not backend_esta_disponible():
    st.warning(
        "No se pudo conectar con el backend (¿está corriendo `uvicorn "
        "backend.main:app --reload`?). Mostrando datos de ejemplo mientras tanto."
    )

if busqueda:
    st.switch_page("pages/comparar_precios.py")

# ---------------------------------------------------------------------
# UBICACIÓN DEL USUARIO
# ---------------------------------------------------------------------
ubicacion = obtener_ubicacion_usuario()

if not ubicacion_es_real():
    st.info(
        "Pidiendo permiso de ubicación a tu navegador... mientras tanto se "
        "muestra una ubicación de referencia (David, Chiriquí)."
    )

tiendas = obtener_tiendas()

# ---------------------------------------------------------------------
# MAPA (folium) + PANELES FLOTANTES
# ---------------------------------------------------------------------
ALTO_MAPA = 620

inyectar_estilos_flotantes(
    paneles={
        "panel_estado": "top-left",
        "panel_acciones": "bottom-right",
        "panel_tienda_sel": "top-right",
    },
    alto_mapa_px=ALTO_MAPA,
)

with st.container(key=MAPA_WRAPPER_KEY):

    mapa = folium.Map(
        location=[ubicacion["lat"], ubicacion["lon"]],
        zoom_start=15,
        tiles="cartodbpositron",
        zoom_control=True,
    )

    folium.Marker(
        location=[ubicacion["lat"], ubicacion["lon"]],
        tooltip="Tú estás aquí",
        icon=folium.Icon(color="red", icon="user", prefix="fa"),
    ).add_to(mapa)

    for _, tienda in tiendas.iterrows():
        popup_html = f"<b>{tienda['nombre']}</b><br>{tienda.get('direccion','')}"
        folium.Marker(
            location=[tienda["lat"], tienda["lon"]],
            tooltip=tienda["nombre"],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color="blue", icon="shopping-cart", prefix="fa"),
        ).add_to(mapa)

    # --- Panel flotante: estado de ubicación (arriba-izquierda) ---
    with st.container(key="panel_estado"):
        if ubicacion_es_real():
            st.caption(f"📍 {ubicacion['lat']:.5f}, {ubicacion['lon']:.5f}")
        else:
            st.caption("📍 Ubicación de referencia")
        st.caption(f"🏬 {len(tiendas)} tienda(s) en el mapa")

    resultado_mapa = st_folium(
        mapa,
        height=ALTO_MAPA,
        use_container_width=True,
        key="mapa_home",
        returned_objects=["last_object_clicked_tooltip"],
    )

    # --- Panel flotante: acciones rápidas (abajo-derecha) ---
    with st.container(key="panel_acciones"):
        if st.button("🔍 Comparar precios", use_container_width=True):
            st.switch_page("pages/comparar_precios.py")
        if st.button("📝 Reportar precio", use_container_width=True):
            st.switch_page("pages/reportar_precio.py")
        if st.button("🛒 Mi lista", use_container_width=True):
            st.switch_page("pages/mi_lista.py")

    # --- Panel flotante: tienda seleccionada + botón de ruta (arriba-derecha) ---
    tooltip_clickeado = resultado_mapa.get("last_object_clicked_tooltip") if resultado_mapa else None
    if tooltip_clickeado:
        tienda_click = tiendas[tiendas["nombre"] == tooltip_clickeado]
        if not tienda_click.empty:
            t = tienda_click.iloc[0]
            with st.container(key="panel_tienda_sel"):
                st.markdown(f"**🏬 {t['nombre']}**")
                st.caption(t.get("direccion", ""))
                if st.button("🧭 Cómo llegar", key="btn_ruta_home", use_container_width=True):
                    st.session_state["ruta_destino"] = {
                        "nombre": t["nombre"],
                        "direccion": t.get("direccion", ""),
                        "lat": t["lat"],
                        "lon": t["lon"],
                    }
                    st.switch_page("pages/ruta.py")