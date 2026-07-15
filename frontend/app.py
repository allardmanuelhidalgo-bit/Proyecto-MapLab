# -*- coding: utf-8 -*-
import base64
import io

import streamlit as st
import pandas as pd

from PIL import Image

from utils import (
    obtener_productos,
    comparar_producto,
    LAT_REFERENCIA,
    LON_REFERENCIA,
)

# Logo (PNG en base64) e iconos SVG viven en assets.py para mantener
# este archivo legible: ver assets.py para el emblema circular de MapLab
# (carrito de compra + pin de mapa) y el set de iconos lineales sin emojis.
from assets import LOGO_B64, ICONOS


def crear_favicon():
    """Icono de la pestaña del navegador, generado desde el mismo logo."""
    return Image.open(io.BytesIO(base64.b64decode(LOGO_B64))).convert("RGBA")


# ==========================================================================
# CONFIGURACION DE PAGINA
# ==========================================================================

st.set_page_config(
    page_title="MapLab",
    page_icon=crear_favicon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================================================
# PALETA
# Todo gira en torno al azul del logo (frio, minimalista). Se combinan
# azules, indigo y cian como acentos creativos. Sin verdes ni rojos en la
# interfaz: las mismas familias de color se usan en tarjetas, grafica y
# tabla para que TODO combine con el logo y sea consistente.
# ==========================================================================

COLOR_TEXT   = "#0F1E33"
COLOR_MUTED  = "#5A6B85"

BRAND_DEEP   = "#0E4C86"   # azul profundo del logo
BRAND        = "#2563EB"   # azul principal
BRAND_LIGHT  = "#3B82F6"
ACCENT_CYAN  = "#06B6D4"
ACCENT_INDIGO= "#4F46E5"
ACCENT_SKY   = "#0EA5E9"

COLOR_BEST   = "#1E50D6"   # barra/insignia del MEJOR precio (la que destaca)

# Tonos frios para el resto de tiendas (todos combinan con el azul del logo)
PALETA_TIENDAS = [
    "#5B8DF0", "#7B7BF0", "#38BDF8", "#9AA8F5",
    "#22D3EE", "#93C5FD", "#B7A6F3", "#60A5FA",
]


def color_por_posicion(indice):
    """Color estable de la paleta fria segun la posicion (orden por precio)."""
    return PALETA_TIENDAS[indice % len(PALETA_TIENDAS)]


def color_por_tienda(nombre_tienda, indice, precio, precio_min):
    """El precio mas bajo se pinta con el azul mas intenso (destaca);
    las demas tiendas usan tonos frios mas suaves de la misma familia."""
    if precio == precio_min:
        return COLOR_BEST
    return color_por_posicion(indice)


# ==========================================================================
# CSS
# ==========================================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

html, body, [class*="css"]{
    font-family:'Manrope', sans-serif;
}

html, body, .stApp{
    color:#0F1E33;
}

header, footer, #MainMenu{
    visibility:hidden;
}

:root, .stApp{
    --primary-color:#2563EB;
}

/* ---------- Fondo dinamico (aurora, misma paleta que tarjetas y badges) ---------- */
.stApp{
    background:
        radial-gradient(circle at 10% 15%, rgba(37,99,235,.48), transparent 40%),
        radial-gradient(circle at 90% 10%, rgba(6,182,212,.42), transparent 38%),
        radial-gradient(circle at 85% 90%, rgba(99,102,241,.40), transparent 42%),
        radial-gradient(circle at 12% 88%, rgba(14,165,233,.38), transparent 40%),
        radial-gradient(circle at 50% 48%, rgba(34,211,238,.22), transparent 55%),
        linear-gradient(135deg,#DCEAFC 0%,#E9F1FE 30%,#EDE8FC 65%,#DCEAFC 100%);
    background-size:340% 340%;
    animation:aurora 24s ease infinite;
}

@keyframes aurora{
    0%{   background-position:0% 30%; }
    25%{  background-position:60% 75%; }
    50%{  background-position:100% 45%; }
    75%{  background-position:45% 10%; }
    100%{ background-position:0% 30%; }
}

.block-container{
    max-width:1120px;
    margin:auto;
    padding:1.2rem 2rem 3rem 2rem;
}

/* ---------- Hero ---------- */
.hero{
    background:rgba(255,255,255,.62);
    backdrop-filter:blur(20px);
    -webkit-backdrop-filter:blur(20px);
    border:1px solid rgba(37,99,235,.10);
    border-radius:28px;
    padding:44px 40px 40px 40px;
    margin-bottom:8px;
    text-align:center;
    box-shadow:0 24px 60px rgba(37,99,235,.12);
}

.logo-wrap{
    display:flex;
    justify-content:center;
    margin-bottom:16px;
    animation:float 6s ease-in-out infinite;
}

/* drop-shadow (filtro) sigue el circulo del logo: sombra redonda, sin recuadro */
.logo-wrap img{
    filter:drop-shadow(0 12px 22px rgba(14,76,134,.28));
}

@keyframes float{
    50%{ transform:translateY(-8px); }
}

.titulo{
    font-family:'Space Grotesk', sans-serif;
    font-size:48px;
    font-weight:700;
    letter-spacing:.5px;
    background:linear-gradient(90deg,#0E4C86,#2563EB,#06B6D4);
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
}

.subtitulo{
    font-size:18px;
    color:#5A6B85;
    max-width:640px;
    margin:12px auto 0 auto;
}

/* ---------- Titulos de seccion (centrados y con aire) ---------- */
.section{
    display:block;
    width:100%;
    text-align:center;
    font-family:'Space Grotesk', sans-serif;
    font-size:26px;
    font-weight:700;
    letter-spacing:.2px;
    color:#0F1E33;
    margin:26px auto 24px auto;
    padding:0;
}

.section::after{
    content:"";
    display:block;
    width:64px;
    height:4px;
    margin:16px auto 0 auto;
    border-radius:99px;
    background:linear-gradient(90deg,#2563EB,#06B6D4);
}

/* Titulo de resultados: mas pegado al boton de busqueda, siempre centrado */
.section-resultado{
    margin-top:2px;
}

/* La linea de color de este titulo sube un poco (menos separacion del
   texto) para dejar mas aire abajo, antes de la marca y las tarjetas. */
.section-resultado::after{
    margin-top:10px;
}

/* ---------- Tarjetas ---------- */
.card{
    background:rgba(255,255,255,.66);
    backdrop-filter:blur(16px);
    -webkit-backdrop-filter:blur(16px);
    border:1px solid rgba(37,99,235,.10);
    border-radius:20px;
    padding:22px;
    text-align:center;
    transition:.26s ease;
    box-shadow:0 14px 34px rgba(37,99,235,.08);
}

.card:hover{
    transform:translateY(-5px);
    border-color:rgba(37,99,235,.32);
    box-shadow:0 20px 44px rgba(37,99,235,.16);
}

.icon-badge{
    width:48px;
    height:48px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    margin:0 auto 14px auto;
    color:#FFFFFF;
}

.badge-azul{   background:linear-gradient(135deg,#2563EB,#1E40AF); box-shadow:0 10px 22px rgba(37,99,235,.30); }
.badge-cian{   background:linear-gradient(135deg,#22D3EE,#0891B2); box-shadow:0 10px 22px rgba(8,145,178,.28); }
.badge-indigo{ background:linear-gradient(135deg,#6366F1,#4338CA); box-shadow:0 10px 22px rgba(79,70,229,.28); }
.badge-cielo{  background:linear-gradient(135deg,#38BDF8,#0EA5E9); box-shadow:0 10px 22px rgba(14,165,233,.28); }

.metric-title{
    font-size:13px;
    letter-spacing:.6px;
    color:#5A6B85;
    text-transform:uppercase;
    text-align:center;
}

.metric-value{
    font-family:'Space Grotesk', sans-serif;
    font-size:30px;
    font-weight:700;
    color:#0F1E33;
    margin-top:4px;
    text-align:center;
}

.metric-sub{
    color:#5A6B85;
    font-size:13px;
    text-align:center;
}

/* ---------- Botones de producto (chips) ---------- */
.stButton button{
    background:rgba(255,255,255,.75);
    border:1.5px solid rgba(37,99,235,.14) !important;
    border-radius:16px;
    min-height:64px;
    color:#0F1E33 !important;
    font-weight:600;
    transition:.22s ease;
    box-shadow:0 8px 22px rgba(37,99,235,.06);
}

.stButton button:hover{
    background:linear-gradient(135deg,#2563EB,#1E40AF);
    border-color:transparent !important;
    color:#FFFFFF !important;
    transform:translateY(-3px);
    box-shadow:0 14px 30px rgba(37,99,235,.28);
}

.stButton button:focus:not(:hover),
.stButton button:active:not(:hover){
    border-color:#2563EB !important;
    color:#0F1E33 !important;
    box-shadow:0 0 0 3px rgba(37,99,235,.16) !important;
}

/* ---------- Formulario ---------- */
div[data-testid="stForm"]{
    background:rgba(255,255,255,.66);
    backdrop-filter:blur(16px);
    -webkit-backdrop-filter:blur(16px);
    border:1px solid rgba(37,99,235,.10);
    border-radius:22px;
    padding:10px 26px 26px 26px;
    box-shadow:0 20px 45px rgba(37,99,235,.12);
    transition:.28s ease;
}

div[data-testid="stForm"]:hover{
    box-shadow:0 26px 55px rgba(37,99,235,.18);
}

div[data-testid="stFormSubmitButton"] button{
    background:linear-gradient(135deg,#2563EB,#1E40AF) !important;
    color:#FFFFFF !important;
    font-weight:700;
    border:none !important;
    border-radius:14px;
    height:54px;
    box-shadow:0 14px 30px rgba(37,99,235,.30);
    transition:.26s ease;
}

div[data-testid="stFormSubmitButton"] button:hover{
    box-shadow:0 18px 40px rgba(37,99,235,.42);
    transform:translateY(-2px);
}

div[data-testid="stFormSubmitButton"] button:focus{
    box-shadow:0 0 0 3px rgba(37,99,235,.25) !important;
}

/* ---------- INPUTS: caja exterior redondeada, borde azul suave ----------
   Se estiliza el contenedor real (baseweb) para eliminar el borde negro
   de esquinas duras y evitar el foco ROJO por defecto de Streamlit. */

/* Contenedor externo del number input (Latitud/Longitud): sin borde/linea
   negra propia, solo se ve el borde azul del baseweb de mas abajo. */
div[data-testid="stNumberInputContainer"],
.stNumberInput > div{
    border:none !important;
    outline:none !important;
    box-shadow:none !important;
    background:transparent !important;
}

.stTextInput div[data-baseweb="input"],
.stTextInput div[data-baseweb="base-input"],
.stNumberInput div[data-baseweb="input"],
.stNumberInput div[data-baseweb="base-input"],
.stSelectbox div[data-baseweb="select"] > div{
    background:#FFFFFF !important;
    border:1.5px solid rgba(37,99,235,.22) !important;
    border-radius:14px !important;
    box-shadow:0 6px 18px rgba(37,99,235,.07) !important;
    transition:border-color .2s ease, box-shadow .2s ease !important;
}

/* al enfocar / hacer clic -> AZUL, nunca rojo */
.stTextInput div[data-baseweb="input"]:focus-within,
.stTextInput div[data-baseweb="base-input"]:focus-within,
.stNumberInput div[data-baseweb="input"]:focus-within,
.stNumberInput div[data-baseweb="base-input"]:focus-within,
.stSelectbox div[data-baseweb="select"]:focus-within > div{
    border-color:#2563EB !important;
    box-shadow:0 0 0 3px rgba(37,99,235,.18) !important;
}

/* input interno: transparente, sin borde ni esquina propia */
.stTextInput input,
.stNumberInput input{
    background:transparent !important;
    border:none !important;
    outline:none !important;
    box-shadow:none !important;
    color:#0F1E33 !important;
}

.stTextInput input::placeholder,
.stNumberInput input::placeholder{
    color:#93A3B8 !important;
    opacity:1;
}

/* Botones +/- del number input */
.stNumberInput button{
    background:#FFFFFF !important;
    border:1.5px solid rgba(37,99,235,.22) !important;
    border-radius:12px !important;
    color:#2563EB !important;
    box-shadow:none !important;
}

.stNumberInput button svg{ fill:#2563EB !important; }

.stNumberInput button:hover,
.stNumberInput button:active,
.stNumberInput button:focus{
    background:#2563EB !important;
    border-color:#2563EB !important;
    color:#FFFFFF !important;
    box-shadow:none !important;
}

.stNumberInput button:hover svg,
.stNumberInput button:active svg,
.stNumberInput button:focus svg{ fill:#FFFFFF !important; }

/* ---------- Etiquetas / desplegable ---------- */
label p,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label{
    color:#0F1E33 !important;
    font-weight:600;
}

div[data-baseweb="select"] *{ color:#0F1E33 !important; }

div[data-baseweb="popover"] li{
    color:#0F1E33 !important;
    background:#FFFFFF !important;
}

div[data-baseweb="popover"] li:hover{ background:#EEF3FF !important; }

/* ---------- Alertas (info / aviso) ---------- */
div[data-testid="stAlert"]{
    background:rgba(37,99,235,.07) !important;
    border:1px solid rgba(37,99,235,.18);
    border-radius:14px;
    box-shadow:0 10px 26px rgba(37,99,235,.08);
}

.stAlert p{ text-align:center; }

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div{ color:#0F1E33 !important; }

.stMarkdown, .stMarkdown p,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
.stCaption{ color:#0F1E33; }

/* ---------- Filas de la tabla comparativa ---------- */
.store-row{
    display:flex;
    align-items:center;
    gap:16px;
    background:rgba(255,255,255,.72);
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
    border:1px solid rgba(37,99,235,.10);
    border-radius:18px;
    padding:14px 20px;
    margin-bottom:10px;
    transition:.24s ease;
}

.store-row:hover{
    transform:translateX(4px);
    border-color:rgba(37,99,235,.28);
    box-shadow:0 14px 30px rgba(37,99,235,.10);
}

.store-logo{
    width:44px;
    height:44px;
    min-width:44px;
    border-radius:12px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#FFFFFF;
    font-weight:800;
    font-size:15px;
    letter-spacing:.3px;
}

.store-info{ flex:1 1 auto; min-width:0; }

.store-name{
    font-weight:700;
    color:#0F1E33;
    font-size:15px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.store-address{
    font-size:12px;
    color:#5A6B85;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.store-bar-wrap{
    width:150px;
    max-width:100%;
    height:7px;
    border-radius:6px;
    background:rgba(37,99,235,.10);
    overflow:hidden;
    margin-top:7px;
}

.store-bar-fill{ height:100%; border-radius:6px; }

/* Grupo derecho: nunca se comprime, evita que precio/distancia/rank se
   amontonen o corten en pantallas angostas o listas largas. */
.store-meta{
    display:flex;
    align-items:center;
    gap:16px;
    flex-shrink:0;
    margin-left:auto;
}

.store-price{
    font-family:'Space Grotesk', sans-serif;
    font-weight:700;
    font-size:18px;
    color:#0F1E33;
    text-align:right;
    white-space:nowrap;
    min-width:64px;
    flex-shrink:0;
}

.store-distance{
    font-size:12px;
    color:#5A6B85;
    text-align:right;
    white-space:nowrap;
    min-width:56px;
    flex-shrink:0;
}

.store-rank{
    font-size:12px;
    font-weight:800;
    border-radius:999px;
    padding:4px 12px;
    min-width:112px;
    text-align:center;
    white-space:nowrap;
    flex-shrink:0;
}

/* ---------- Ajuste responsivo de la tabla comparativa ---------- */
@media (max-width:640px){
    .store-row{
        flex-wrap:wrap;
        padding:14px 16px;
        row-gap:12px;
    }
    .store-info{ flex:1 1 calc(100% - 60px); }
    .store-meta{
        flex:1 1 100%;
        justify-content:space-between;
        margin-left:60px;
        gap:10px;
    }
    .store-price{ font-size:16px; min-width:52px; }
    .store-distance{ min-width:46px; }
    .store-rank{ min-width:92px; }
}

</style>
""", unsafe_allow_html=True)

# ==========================================================================
# HERO
# ==========================================================================

st.markdown(f"""
<div class="hero">
    <div class="logo-wrap">
        <img src="data:image/png;base64,{LOGO_B64}" width="104" height="104" alt="MapLab"/>
    </div>
    <div class="titulo">MAPLAB</div>
    <div class="subtitulo">Comparador inteligente de precios entre supermercados cercanos.</div>
</div>
""", unsafe_allow_html=True)

# ==========================================================================
# ESTADO DE SESION
# ==========================================================================

st.session_state.setdefault("nombre_input", "")
st.session_state.setdefault("resultado", None)
st.session_state.setdefault("error_msg", None)
st.session_state.setdefault("lat_buscada", LAT_REFERENCIA)
st.session_state.setdefault("lon_buscada", LON_REFERENCIA)

# ==========================================================================
# PRODUCTOS DISPONIBLES
# ==========================================================================

productos = obtener_productos()

if productos:
    st.markdown('<div class="section">Productos disponibles</div>', unsafe_allow_html=True)

    nombres = []
    for p in productos:
        nombre = p.get("nombre")
        if nombre and nombre not in nombres:
            nombres.append(nombre)
    nombres = nombres[:8]

    columnas = st.columns(4, gap="medium")
    for i, nombre in enumerate(nombres):
        with columnas[i % 4]:
            if st.button(nombre, use_container_width=True, key=f"producto_{i}"):
                st.session_state.nombre_input = nombre
                st.rerun()

# ==========================================================================
# FORMULARIO DE BUSQUEDA
# ==========================================================================

st.markdown('<div class="section">Buscar producto</div>', unsafe_allow_html=True)

with st.form("buscar_producto"):
    c1, c2 = st.columns([3, 1])
    with c1:
        nombre_producto = st.text_input(
            "Producto",
            placeholder="Ejemplo: Leche, Arroz, Aceite...",
            key="nombre_input",
        )
    with c2:
        limite = st.selectbox("Tiendas", [2, 3, 4, 5, 6, 7, 8], index=0)

    c3, c4 = st.columns(2)
    with c3:
        lat = st.number_input("Latitud", value=LAT_REFERENCIA, format="%.6f")
    with c4:
        lon = st.number_input("Longitud", value=LON_REFERENCIA, format="%.6f")

    st.info("Puedes usar las coordenadas por defecto o ingresar tu ubicacion.")

    buscar = st.form_submit_button("Buscar mejores precios", use_container_width=True)

# ==========================================================================
# CONSULTA A LA API
# ==========================================================================

if buscar:
    if nombre_producto.strip() == "":
        st.warning("Debes escribir un producto.")
    else:
        with st.spinner("Buscando supermercados cercanos..."):
            datos, error = comparar_producto(nombre_producto.strip(), lat, lon, limite=limite)

        st.session_state.resultado = datos
        st.session_state.error_msg = error
        st.session_state.lat_buscada = lat
        st.session_state.lon_buscada = lon

# ==========================================================================
# RESULTADOS
# ==========================================================================

resultado = st.session_state.resultado
error_msg = st.session_state.error_msg

if resultado is None and error_msg is None:

    # Estado vacio: guiamos al usuario en vez de dejar la pantalla en blanco.
    st.markdown('<div class="section">Como funciona</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3, gap="medium")
    pasos = [
        (p1, "badge-azul",   "search", "1. Busca",   "Escribe un producto o elige uno de la lista de arriba."),
        (p2, "badge-cielo",  "chart",  "2. Compara", "Revisa precios y distancias de las tiendas cercanas."),
        (p3, "badge-indigo", "coin",   "3. Ahorra",  "Elige la mejor opcion entre precio y cercania."),
    ]
    for col, badge, icono_key, titulo_paso, texto in pasos:
        with col:
            st.markdown(f"""
            <div class="card" style="min-height:170px;">
                <div class="icon-badge {badge}">{ICONOS[icono_key]}</div>
                <div class="metric-title">{titulo_paso}</div>
                <div class="metric-sub" style="margin-top:8px;">{texto}</div>
            </div>
            """, unsafe_allow_html=True)

elif resultado is None:
    st.error(error_msg)

else:
    precios = resultado.get("precios", [])

    if len(precios) == 0:
        st.warning("No existen precios registrados.")
    else:
        df = pd.DataFrame(precios)
        df["precio"] = pd.to_numeric(df["precio"])
        df["distancia_km"] = pd.to_numeric(df["distancia_km"])

        idx_barato = df["precio"].idxmin()
        idx_cercano = df["distancia_km"].idxmin()
        mejor = df.loc[idx_barato]
        cercano = df.loc[idx_cercano]

        precio_max = df["precio"].max()
        precio_min = df["precio"].min()
        ahorro = precio_max - precio_min
        ahorro_pct = (ahorro / precio_max * 100) if precio_max > 0 else 0

        st.markdown(
            f'<div class="section section-resultado">Resultado para: {resultado["producto_nombre"]}</div>',
            unsafe_allow_html=True,
        )
        if resultado.get("marca"):
            st.markdown(
                '<div style="display:block;width:100%;text-align:center;color:#5A6B85;'
                'margin:-10px auto 26px auto;">'
                f"Marca: <strong>{resultado['marca']}</strong></div>",
                unsafe_allow_html=True,
            )

        # -------- 4 tarjetas de metricas (mismo tamano) --------
        c1, c2, c3, c4 = st.columns(4, gap="medium")

        with c1:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-azul">{ICONOS['tag']}</div>
                <div class="metric-title">Precio mas bajo</div>
                <div class="metric-value">${mejor['precio']:.2f}</div>
                <div class="metric-sub">{mejor['tienda_nombre']}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-cian">{ICONOS['pin']}</div>
                <div class="metric-title">Tienda mas cercana</div>
                <div class="metric-value">{cercano['distancia_km']:.2f} km</div>
                <div class="metric-sub">{cercano['tienda_nombre']}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-indigo">{ICONOS['percent']}</div>
                <div class="metric-title">Ahorro potencial</div>
                <div class="metric-value">${ahorro:.2f}</div>
                <div class="metric-sub">{ahorro_pct:.0f}% vs. el mas caro</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-cielo">{ICONOS['store']}</div>
                <div class="metric-title">Tiendas comparadas</div>
                <div class="metric-value">{len(df)}</div>
                <div class="metric-sub">en la zona</div>
            </div>
            """, unsafe_allow_html=True)

        # -------- Tabla comparativa --------
        st.markdown('<div class="section">Tabla comparativa</div>', unsafe_allow_html=True)

        df_tabla = df.sort_values("precio", ascending=True).reset_index(drop=True)

        filas_html = []
        for i, fila in df_tabla.iterrows():
            es_mejor = fila["precio"] == precio_min
            color = color_por_tienda(fila["tienda_nombre"], i, fila["precio"], precio_min)

            palabras = str(fila["tienda_nombre"]).split()
            iniciales = "".join(p[0] for p in palabras[:2]).upper() or "T"

            ancho_barra = (fila["precio"] / precio_max * 100) if precio_max > 0 else 0
            ancho_barra = max(6, min(100, ancho_barra))

            pill_bg = COLOR_BEST if es_mejor else "rgba(37,99,235,.10)"
            pill_color = "#FFFFFF" if es_mejor else "#5A6B85"
            pill_texto = "Mejor precio" if es_mejor else f"#{i + 1}"

            filas_html.append(f"""
            <div class="store-row">
                <div class="store-logo" style="background:{color};">{iniciales}</div>
                <div class="store-info">
                    <div class="store-name">{fila['tienda_nombre']}</div>
                    <div class="store-address">{fila['direccion']}</div>
                    <div class="store-bar-wrap">
                        <div class="store-bar-fill" style="width:{ancho_barra:.0f}%;background:{color};"></div>
                    </div>
                </div>
                <div class="store-meta">
                    <div class="store-price">${fila['precio']:.2f}</div>
                    <div class="store-distance">{fila['distancia_km']:.2f} km</div>
                    <div class="store-rank" style="background:{pill_bg};color:{pill_color};">{pill_texto}</div>
                </div>
            </div>
            """)

        st.markdown("".join(filas_html), unsafe_allow_html=True)

        st.markdown(
            '<div style="text-align:center;color:#5A6B85;font-size:14px;margin-top:8px;">'
            f"Precio promedio: <strong>${df['precio'].mean():.2f}</strong> &middot; "
            f"Distancia promedio: <strong>{df['distancia_km'].mean():.2f} km</strong></div>",
            unsafe_allow_html=True,
        )

        # -------- Mapa --------
        st.markdown('<div class="section">Ubicacion de referencia</div>', unsafe_allow_html=True)
        st.map(
            pd.DataFrame([{
                "lat": st.session_state.lat_buscada,
                "lon": st.session_state.lon_buscada,
            }]),
            size=180,
            color="#2563EB",
            zoom=15,
        )

# ==========================================================================
# FOOTER
# ==========================================================================

st.markdown('<hr style="margin:8px 0 4px 0;">', unsafe_allow_html=True)
st.markdown("""
<div style="display:block;width:100%;text-align:center;padding:6px 0 14px 0;opacity:.75;">
    <h4 style="letter-spacing:1px;margin-bottom:4px;font-family:'Space Grotesk',sans-serif;color:#0E4C86;">MAPLAB</h4>
    <p style="margin:2px 0;">Comparador inteligente de precios</p>
    <p style="margin:2px 0;font-size:13px;">Desarrollado con Streamlit y FastAPI</p>
</div>
""", unsafe_allow_html=True)