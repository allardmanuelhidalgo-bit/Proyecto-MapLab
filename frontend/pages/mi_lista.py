# frontend/pages/mi_lista.py
#
# Lista personal de productos del usuario: agregar, marcar comprado y quitar.
# Usa los endpoints GET/POST /listas y PATCH/DELETE /listas/{item_id}.

import streamlit as st
from elements.header import render_header
from utils import usuario_actual, obtener_lista, agregar_a_lista, marcar_comprado, quitar_de_lista, BACKEND_URL
import requests

st.set_page_config(page_title="MapLab - Mi lista", page_icon="🛒", layout="wide")
render_header()

st.subheader("Mi lista de compras")

usuario = usuario_actual()
if usuario is None:
    st.warning("Identifícate primero (arriba a la derecha) para ver y armar tu lista personal.")
    st.stop()

# --- Agregar producto a la lista ---
try:
    productos = requests.get(f"{BACKEND_URL}/productos", timeout=5).json()
except Exception:
    productos = []

with st.container(border=True):
    st.markdown("**Agregar producto a la lista**")
    if not productos:
        st.info("No hay productos registrados todavía. Ve a 'Reportar precio' para dar de alta uno.")
    else:
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            producto_sel = st.selectbox(
                "Producto", productos,
                format_func=lambda p: f"{p['nombre']}" + (f" ({p['marca']})" if p.get("marca") else ""),
                label_visibility="collapsed",
            )
        with col_btn:
            if st.button("➕ Agregar", use_container_width=True):
                ok, msg = agregar_a_lista(usuario["id"], producto_sel["id"])
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

st.markdown("---")

# --- Ver / gestionar la lista ---
items = obtener_lista(usuario["id"])

if not items:
    st.info("Tu lista está vacía por ahora.")
else:
    pendientes = [i for i in items if not i["comprado"]]
    comprados = [i for i in items if i["comprado"]]

    st.markdown(f"**Pendientes ({len(pendientes)})**")
    for item in pendientes:
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.write(f"🔲 {item['producto_nombre']}" + (f" ({item['marca']})" if item.get("marca") else ""))
        with c2:
            if st.button("✅ Comprado", key=f"comprado_{item['id']}"):
                if marcar_comprado(item["id"], True):
                    st.rerun()
        with c3:
            if st.button("🗑️ Quitar", key=f"quitar_{item['id']}"):
                if quitar_de_lista(item["id"]):
                    st.rerun()

    if comprados:
        st.markdown(f"**Ya comprados ({len(comprados)})**")
        for item in comprados:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(f"✅ ~~{item['producto_nombre']}~~")
            with c2:
                if st.button("↩️ Deshacer", key=f"deshacer_{item['id']}"):
                    if marcar_comprado(item["id"], False):
                        st.rerun()
            with c3:
                if st.button("🗑️ Quitar", key=f"quitar2_{item['id']}"):
                    if quitar_de_lista(item["id"]):
                        st.rerun()
