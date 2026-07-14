# frontend/pages/reportar_precio.py
#
# Permite a un usuario reportar el precio que vio de un producto en una
# tienda (POST /precios), y da atajos para dar de alta un producto o una
# tienda que todavía no existan en el catálogo (POST /productos, POST /tiendas).

import streamlit as st
from elements.header import render_header
from utils import (
    listar_categorias,
    crear_producto,
    crear_tienda,
    registrar_precio,
    usuario_actual,
    obtener_ubicacion_usuario,
    BACKEND_URL,
)
import requests

st.set_page_config(page_title="MapLab - Reportar precio", page_icon="📝", layout="wide")
render_header()

st.subheader("Reportar un precio")

usuario = usuario_actual()
if usuario is None:
    st.warning("Identifícate primero (arriba a la derecha) para que tu reporte quede a tu nombre. Puedes seguir, pero el reporte quedará anónimo.")

tab_reportar, tab_producto_nuevo, tab_tienda_nueva = st.tabs(
    ["Reportar precio", "Registrar producto nuevo", "Registrar tienda nueva"]
)

# ---------------------------------------------------------------------
# TAB 1: Reportar precio de un producto/tienda ya existentes
# ---------------------------------------------------------------------
with tab_reportar:
    try:
        productos = requests.get(f"{BACKEND_URL}/productos", timeout=5).json()
    except Exception:
        productos = []
    try:
        tiendas = requests.get(f"{BACKEND_URL}/tiendas", timeout=5).json()
    except Exception:
        tiendas = []

    if not productos or not tiendas:
        st.info("Todavía no hay productos o tiendas registradas. Usa las otras pestañas para crear el producto/tienda primero.")
    else:
        producto_sel = st.selectbox(
            "Producto", productos, format_func=lambda p: f"{p['nombre']}" + (f" ({p['marca']})" if p.get("marca") else "")
        )
        tienda_sel = st.selectbox("Tienda", tiendas, format_func=lambda t: t["nombre"])
        precio = st.number_input("Precio visto ($)", min_value=0.01, step=0.01, format="%.2f")

        if st.button("Enviar reporte", type="primary"):
            ok, resultado = registrar_precio(
                producto_sel["id"], tienda_sel["id"], precio, usuario["id"] if usuario else None
            )
            if ok:
                st.success(f"¡Gracias! Reportaste ${precio:.2f} para {producto_sel['nombre']} en {tienda_sel['nombre']}.")
            else:
                st.error(f"No se pudo registrar: {resultado}")

# ---------------------------------------------------------------------
# TAB 2: Registrar producto nuevo
# ---------------------------------------------------------------------
with tab_producto_nuevo:
    categorias = listar_categorias()
    if not categorias:
        st.warning("No se pudieron cargar las categorías desde el backend.")
    else:
        nombre_prod = st.text_input("Nombre del producto", key="nuevo_prod_nombre")
        marca_prod = st.text_input("Marca (opcional)", key="nuevo_prod_marca")
        categoria_sel = st.selectbox("Categoría", categorias, format_func=lambda c: c["nombre"], key="nuevo_prod_categoria")

        if st.button("Registrar producto", key="btn_nuevo_producto"):
            if not nombre_prod:
                st.warning("Escribe el nombre del producto.")
            else:
                ok, resultado = crear_producto(nombre_prod, categoria_sel["id"], marca_prod or None)
                if ok:
                    st.success(f"Producto '{resultado['nombre']}' registrado.")
                else:
                    st.error(f"No se pudo registrar: {resultado}")

# ---------------------------------------------------------------------
# TAB 3: Registrar tienda nueva (usa tu ubicación actual como punto de partida)
# ---------------------------------------------------------------------
with tab_tienda_nueva:
    ubicacion = obtener_ubicacion_usuario(pedir_si_falta=False)
    st.caption("Por defecto usamos tu ubicación actual; ajústala si la tienda está en otro lugar.")

    nombre_tienda = st.text_input("Nombre de la tienda", key="nueva_tienda_nombre")
    direccion_tienda = st.text_input("Dirección", key="nueva_tienda_direccion")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat_tienda = st.number_input("Latitud", value=ubicacion["lat"], format="%.6f")
    with col_lon:
        lon_tienda = st.number_input("Longitud", value=ubicacion["lon"], format="%.6f")

    if st.button("Registrar tienda", key="btn_nueva_tienda"):
        if not nombre_tienda:
            st.warning("Escribe el nombre de la tienda.")
        else:
            ok, resultado = crear_tienda(nombre_tienda, direccion_tienda, lat_tienda, lon_tienda)
            if ok:
                st.success(f"Tienda '{resultado['nombre']}' registrada.")
            else:
                st.error(f"No se pudo registrar: {resultado}")
