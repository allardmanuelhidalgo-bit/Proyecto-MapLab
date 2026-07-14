# frontend/pages/ruta.py
#
# Traza una ruta desde la ubicación del usuario hasta una tienda,
# como un GPS: mapa con la línea de la ruta, distancia, duración y
# pasos de navegación. Usa el motor de ruteo OSRM (utils.calcular_ruta).

import folium
import streamlit as st
from streamlit_folium import st_folium

from elements.header import render_header
from elements.floating import inyectar_estilos_flotantes, MAPA_WRAPPER_KEY
from utils import obtener_tiendas, obtener_ubicacion_usuario, calcular_ruta

st.set_page_config(page_title="MapLab - Cómo llegar", page_icon="🧭", layout="wide")
render_header()

st.subheader("Cómo llegar")

# --- Tienda destino: viene de session_state (click en el mapa de home)
#     o se elige aquí mismo si se entra directo a esta página. ---
destino_guardado = st.session_state.get("ruta_destino")

tiendas = obtener_tiendas()
if tiendas.empty:
    st.warning("No hay tiendas registradas todavía.")
    st.stop()

opciones = tiendas.to_dict("records")
indice_default = 0
if destino_guardado:
    for i, t in enumerate(opciones):
        if t["nombre"] == destino_guardado["nombre"]:
            indice_default = i
            break

tienda_sel = st.selectbox(
    "Tienda de destino",
    opciones,
    index=indice_default,
    format_func=lambda t: f"{t['nombre']} — {t.get('direccion','')}",
)

perfil = st.radio("Medio de transporte", ["carro", "a_pie", "bici"], horizontal=True,
                   format_func=lambda p: {"carro": "🚗 Carro", "a_pie": "🚶 A pie", "bici": "🚴 Bici"}[p])

ubicacion = obtener_ubicacion_usuario()
destino = {"lat": tienda_sel["lat"], "lon": tienda_sel["lon"]}

ruta = calcular_ruta(ubicacion, destino, perfil)

ALTO_MAPA = 550
inyectar_estilos_flotantes(paneles={"panel_resumen": "top-left"}, alto_mapa_px=ALTO_MAPA)

with st.container(key=MAPA_WRAPPER_KEY):
    mapa = folium.Map(location=[ubicacion["lat"], ubicacion["lon"]], zoom_start=14, tiles="cartodbpositron")

    folium.Marker([ubicacion["lat"], ubicacion["lon"]], tooltip="Origen",
                  icon=folium.Icon(color="red", icon="user", prefix="fa")).add_to(mapa)
    folium.Marker([destino["lat"], destino["lon"]], tooltip=tienda_sel["nombre"],
                  icon=folium.Icon(color="blue", icon="shopping-cart", prefix="fa")).add_to(mapa)

    if ruta:
        folium.plugins.AntPath(
            locations=ruta["puntos"],
            color="#1E88E5",
            weight=5,
            delay=800,
        ).add_to(mapa)
        mapa.fit_bounds(ruta["puntos"])
    else:
        # Sin ruta real disponible: al menos mostramos una línea recta
        folium.PolyLine(
            [[ubicacion["lat"], ubicacion["lon"]], [destino["lat"], destino["lon"]]],
            color="#9E9E9E", weight=3, dash_array="8",
        ).add_to(mapa)
        mapa.fit_bounds([[ubicacion["lat"], ubicacion["lon"]], [destino["lat"], destino["lon"]]])

    with st.container(key="panel_resumen"):
        if ruta:
            st.metric("Distancia", f"{ruta['distancia_km']} km")
            st.metric("Tiempo estimado", f"{ruta['duracion_min']} min")
        else:
            st.caption("⚠️ No se pudo calcular la ruta real (sin conexión al servicio de ruteo). Mostrando línea directa.")

    st_folium(mapa, height=ALTO_MAPA, use_container_width=True, key="mapa_ruta")

st.markdown("---")

if ruta and ruta["pasos"]:
    st.markdown("**Pasos de la ruta:**")
    for i, paso in enumerate(ruta["pasos"], start=1):
        st.write(f"{i}. {paso}")