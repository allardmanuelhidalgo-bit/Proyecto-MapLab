# frontend/app.py
#
# MapLab - vista única (Home).
#
# Toda la app vive en este único archivo. No hay login ni multipágina:
# solo un mapa con la ubicación del usuario y paneles flotantes que se
# abren y cierran según lo que el usuario cliquea:
#
#   - panel_estado      (arriba-izquierda): ubicación real + nº de tiendas.
#   - panel_resultados  (arriba-centro):    aparece al buscar un producto;
#                                            compara precio y tienda, con
#                                            botón "Cómo llegar" por fila.
#   - panel_tienda      (arriba-derecha):   aparece al hacer click en un
#                                            marcador de tienda en el mapa.
#   - panel_ruta        (abajo-izquierda):  aparece al pedir "Cómo llegar";
#                                            muestra distancia, tiempo y
#                                            pasos, dibuja la ruta en el
#                                            mismo mapa.

import folium
import streamlit as st
from streamlit_folium import st_folium

from elements.header import render_header
from elements.floating import inyectar_estilos_flotantes, MAPA_WRAPPER_KEY
from utils import (
    obtener_tiendas,
    backend_esta_disponible,
    obtener_ubicacion_usuario,
    ubicacion_es_real,
    comparar_producto,
    calcular_ruta,
)

st.set_page_config(
    page_title="MapLab - Comparador de precios",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Sin sidebar: es una app de una sola vista, no hace falta navegación
# lateral. Ocultamos tanto el contenedor como la flecha para expandirla.
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# ESTADO DE LOS PANELES
# ---------------------------------------------------------------------
st.session_state.setdefault("resultados_cerrado", False)
st.session_state.setdefault("tienda_seleccionada", None)
st.session_state.setdefault("mostrar_ruta", False)
st.session_state.setdefault("ruta_destino", None)
st.session_state.setdefault("ruta_perfil", "carro")
st.session_state.setdefault("ultima_busqueda", "")

busqueda = render_header()

if not backend_esta_disponible():
    st.warning(
        "No se pudo conectar con el backend (¿está corriendo `uvicorn "
        "backend.main:app --reload`?). Mostrando datos de ejemplo mientras tanto."
    )

# Nueva búsqueda -> reabre el panel de resultados aunque lo hayan cerrado antes
if busqueda and busqueda != st.session_state["ultima_busqueda"]:
    st.session_state["ultima_busqueda"] = busqueda
    st.session_state["resultados_cerrado"] = False

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
# BUSCAR / COMPARAR PRECIOS (dispara el panel_resultados)
# ---------------------------------------------------------------------
resultado_comparacion = None
error_comparacion = None
if busqueda:
    ok, resultado = comparar_producto(busqueda, ubicacion["lat"], ubicacion["lon"], limite=8)
    if ok:
        resultado_comparacion = resultado
    else:
        error_comparacion = resultado

# ---------------------------------------------------------------------
# RUTA (si el usuario pidió "Cómo llegar")
# ---------------------------------------------------------------------
ruta = None
if st.session_state["mostrar_ruta"] and st.session_state["ruta_destino"]:
    destino = st.session_state["ruta_destino"]
    ruta = calcular_ruta(
        ubicacion,
        {"lat": destino["lat"], "lon": destino["lon"]},
        st.session_state["ruta_perfil"],
    )


def _iniciar_ruta(nombre: str, direccion: str, lat: float, lon: float):
    st.session_state["ruta_destino"] = {
        "nombre": nombre, "direccion": direccion, "lat": lat, "lon": lon,
    }
    st.session_state["mostrar_ruta"] = True


# ---------------------------------------------------------------------
# MAPA + PANELES FLOTANTES
# ---------------------------------------------------------------------
ALTO_MAPA = 640

inyectar_estilos_flotantes(
    paneles={
        "panel_estado": "top-left",
        "panel_resultados": "top-center",
        "panel_tienda": "top-right",
        "panel_ruta": "bottom-left",
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

    destino_activo = st.session_state["ruta_destino"] if st.session_state["mostrar_ruta"] else None

    for _, tienda in tiendas.iterrows():
        es_destino = destino_activo is not None and tienda["nombre"] == destino_activo["nombre"]
        popup_html = f"<b>{tienda['nombre']}</b><br>{tienda.get('direccion','')}"
        folium.Marker(
            location=[tienda["lat"], tienda["lon"]],
            tooltip=tienda["nombre"],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color="green" if es_destino else "blue", icon="shopping-cart", prefix="fa"),
        ).add_to(mapa)

    # --- Ruta dibujada sobre el mismo mapa ---
    if st.session_state["mostrar_ruta"] and destino_activo:
        if ruta:
            folium.plugins.AntPath(
                locations=ruta["puntos"],
                color="#1E88E5",
                weight=5,
                delay=800,
            ).add_to(mapa)
            mapa.fit_bounds(ruta["puntos"])
        else:
            folium.PolyLine(
                [[ubicacion["lat"], ubicacion["lon"]], [destino_activo["lat"], destino_activo["lon"]]],
                color="#9E9E9E", weight=3, dash_array="8",
            ).add_to(mapa)
            mapa.fit_bounds([
                [ubicacion["lat"], ubicacion["lon"]],
                [destino_activo["lat"], destino_activo["lon"]],
            ])

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

    # --- Panel flotante: resultados de la búsqueda (arriba-centro) ---
    if busqueda and not st.session_state["resultados_cerrado"]:
        with st.container(key="panel_resultados"):
            c_titulo, c_cerrar = st.columns([5, 1])
            with c_titulo:
                st.markdown("**🔍 Comparar precios**")
            with c_cerrar:
                if st.button("✕", key="cerrar_resultados", help="Cerrar"):
                    st.session_state["resultados_cerrado"] = True
                    st.rerun()

            if error_comparacion:
                st.warning(f"No se encontró '{busqueda}': {error_comparacion}")
            elif resultado_comparacion:
                precios = sorted(resultado_comparacion["precios"], key=lambda p: float(p["precio"]))
                titulo = resultado_comparacion["producto_nombre"]
                if resultado_comparacion.get("marca"):
                    titulo += f" — {resultado_comparacion['marca']}"
                st.caption(titulo)

                for p in precios:
                    st.markdown(f"**🏬 {p['tienda_nombre']}**")
                    st.caption(p.get("direccion") or "Sin dirección registrada")
                    c1, c2, c3 = st.columns([1, 1, 1.3])
                    with c1:
                        st.metric("Precio", f"${float(p['precio']):.2f}", label_visibility="collapsed")
                    with c2:
                        st.caption(f"📏 {p['distancia_km']} km")
                    with c3:
                        if st.button("🧭 Ir", key=f"ir_{p['precio_id']}", use_container_width=True):
                            _iniciar_ruta(p["tienda_nombre"], p.get("direccion", ""), p["latitud"], p["longitud"])
                            st.rerun()
                    st.divider()

    # --- Panel flotante: tienda seleccionada en el mapa (arriba-derecha) ---
    tooltip_clickeado = resultado_mapa.get("last_object_clicked_tooltip") if resultado_mapa else None
    if tooltip_clickeado:
        tienda_click = tiendas[tiendas["nombre"] == tooltip_clickeado]
        if not tienda_click.empty:
            st.session_state["tienda_seleccionada"] = tienda_click.iloc[0].to_dict()

    tienda_sel = st.session_state["tienda_seleccionada"]
    if tienda_sel:
        with st.container(key="panel_tienda"):
            c_titulo, c_cerrar = st.columns([5, 1])
            with c_titulo:
                st.markdown(f"**🏬 {tienda_sel['nombre']}**")
            with c_cerrar:
                if st.button("✕", key="cerrar_tienda", help="Cerrar"):
                    st.session_state["tienda_seleccionada"] = None
                    st.rerun()
            st.caption(tienda_sel.get("direccion", ""))
            if st.button("🧭 Cómo llegar", key="btn_ruta_tienda", use_container_width=True):
                _iniciar_ruta(tienda_sel["nombre"], tienda_sel.get("direccion", ""), tienda_sel["lat"], tienda_sel["lon"])
                st.rerun()

    # --- Panel flotante: ruta activa (abajo-izquierda) ---
    if st.session_state["mostrar_ruta"] and destino_activo:
        with st.container(key="panel_ruta"):
            c_titulo, c_cerrar = st.columns([5, 1])
            with c_titulo:
                st.markdown(f"**🧭 Ruta a {destino_activo['nombre']}**")
            with c_cerrar:
                if st.button("✕", key="cerrar_ruta", help="Cerrar"):
                    st.session_state["mostrar_ruta"] = False
                    st.session_state["ruta_destino"] = None
                    st.rerun()

            perfil_nombres = {"carro": "🚗 Carro", "a_pie": "🚶 A pie", "bici": "🚴 Bici"}
            nuevo_perfil = st.radio(
                "Medio de transporte",
                list(perfil_nombres.keys()),
                index=list(perfil_nombres.keys()).index(st.session_state["ruta_perfil"]),
                format_func=lambda p: perfil_nombres[p],
                horizontal=True,
                key="radio_perfil_ruta",
                label_visibility="collapsed",
            )
            if nuevo_perfil != st.session_state["ruta_perfil"]:
                st.session_state["ruta_perfil"] = nuevo_perfil
                st.rerun()

            if ruta:
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Distancia", f"{ruta['distancia_km']} km")
                with c2:
                    st.metric("Tiempo", f"{ruta['duracion_min']} min")
                if ruta["pasos"]:
                    st.caption("**Pasos:**")
                    for i, paso in enumerate(ruta["pasos"], start=1):
                        st.caption(f"{i}. {paso}")
            else:
                st.caption(
                    "⚠️ No se pudo calcular la ruta real (sin conexión al "
                    "servicio de ruteo). Mostrando línea directa."
                )