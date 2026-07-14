# frontend/pages/comparar_precios.py
#
# Vista principal de MapLab: buscar un producto y comparar su precio
# en las tiendas más cercanas (RF1 + RF2), con opción de ordenar por
# precio o por distancia, y votar si un precio reportado sigue vigente.

import streamlit as st
from elements.header import render_header
from utils import (
    comparar_producto,
    obtener_ubicacion_usuario,
    ubicacion_es_real,
    usuario_actual,
    votar_precio,
)

st.set_page_config(
    page_title="MapLab - Comparar precios",
    page_icon="🗺️",
    layout="wide",
)

busqueda_header = render_header()

st.subheader("Comparar precios")

# La búsqueda puede venir del header (otra página) o escribirse aquí mismo
termino = st.text_input(
    "¿Qué producto buscas?",
    value=busqueda_header or st.session_state.get("busqueda", ""),
    placeholder="Ej: leche, arroz, detergente...",
)

col_orden, col_limite = st.columns([1, 1])
with col_orden:
    orden = st.radio("Ordenar por", ["Precio (menor a mayor)", "Cercanía"], horizontal=True)
with col_limite:
    limite = st.slider("Cuántas tiendas mostrar", min_value=2, max_value=10, value=5)

ubicacion = obtener_ubicacion_usuario()
if not ubicacion_es_real():
    st.caption(
        "⚠️ Todavía no tengo tu ubicación real (falta el permiso del navegador); "
        "las distancias se calculan desde una ubicación de referencia mientras tanto."
    )

if termino:
    ok, resultado = comparar_producto(termino, ubicacion["lat"], ubicacion["lon"], limite)

    if not ok:
        st.error(f"No se pudo comparar: {resultado}")
    else:
        precios = resultado["precios"]

        if orden == "Precio (menor a mayor)":
            precios = sorted(precios, key=lambda p: float(p["precio"]))
        else:
            precios = sorted(precios, key=lambda p: p["distancia_km"])

        st.markdown(f"### {resultado['producto_nombre']}" + (f" — *{resultado['marca']}*" if resultado.get("marca") else ""))
        st.caption(f"{len(precios)} tienda(s) encontradas, ordenadas por {orden.lower()}")

        usuario = usuario_actual()

        for p in precios:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**🏬 {p['tienda_nombre']}**")
                    st.caption(p.get("direccion") or "Sin dirección registrada")
                with c2:
                    st.metric("Precio", f"${float(p['precio']):.2f}")
                with c3:
                    st.metric("Distancia", f"{p['distancia_km']} km")

                voto_col1, voto_col2, voto_col3 = st.columns([1, 1, 3])
                with voto_col1:
                    if st.button("👍 Vigente", key=f"si_{p['precio_id']}", use_container_width=True):
                        if usuario is None:
                            st.warning("Identifícate primero para poder votar (botón en el header o página de inicio).")
                        else:
                            ok_v, msg = votar_precio(p["precio_id"], usuario["id"], True)
                            st.toast(msg) if ok_v else st.error(msg)
                with voto_col2:
                    if st.button("👎 Ya no", key=f"no_{p['precio_id']}", use_container_width=True):
                        if usuario is None:
                            st.warning("Identifícate primero para poder votar (botón en el header o página de inicio).")
                        else:
                            ok_v, msg = votar_precio(p["precio_id"], usuario["id"], False)
                            st.toast(msg) if ok_v else st.error(msg)
                with voto_col3:
                    st.caption(f"👍 {p['votos_a_favor']}  ·  👎 {p['votos_en_contra']}  ·  reportado {p['fecha_registro'][:10]}")
else:
    st.info("Escribe el nombre de un producto para comparar precios cercanos.")
