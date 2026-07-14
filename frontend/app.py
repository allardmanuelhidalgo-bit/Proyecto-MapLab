import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    obtener_productos,
    comparar_producto,
    LAT_REFERENCIA,
    LON_REFERENCIA,
)

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================

st.set_page_config(
    page_title="MapLab",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# PALETA (usada también en los gráficos de Plotly
# para que combinen exactamente con el resto de la app)
# ==========================================

COLOR_BG = "#0B1220"
COLOR_AMBER = "#F5A524"   # acento principal — mejor precio, CTA
COLOR_TEAL = "#2DD4BF"    # acento secundario — ubicación / positivo
COLOR_CORAL = "#FB7185"   # acento de atención — ahorro
COLOR_TEXT = "#EAF0FB"
COLOR_MUTED = "#93A1B7"
COLOR_BAR_MUTED = "#3B4A63"

# ==========================================
# ICONOS DE PRODUCTOS (se usan como "sticker" en las cards)
# ==========================================

PRODUCTOS_ICONOS = {
    "leche": "🥛",
    "arroz": "🍚",
    "queso": "🧀",
    "cafe": "☕",
    "café": "☕",
    "aceite": "🛢️",
    "azucar": "🍬",
    "azúcar": "🍬",
    "detergente": "🧴",
    "jabon": "🧼",
    "jabón": "🧼",
    "pollo": "🍗",
    "huevo": "🥚",
    "atun": "🐟",
    "atún": "🐟",
    "pan": "🍞",
    "agua": "💧",
    "gaseosa": "🥤",
    "sal": "🧂",
}


def obtener_icono(nombre):
    nombre = nombre.lower()
    for palabra, icono in PRODUCTOS_ICONOS.items():
        if palabra in nombre:
            return icono
    return "🛒"


# ==========================================
# CSS
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

:root{
    --glass-bg: rgba(255,255,255,.06);
    --glass-border: rgba(255,255,255,.12);
    --panel-bg: #141C2E;
    --accent-amber: #F5A524;
    --accent-teal: #2DD4BF;
    --accent-coral: #FB7185;
    --text-primary: #EAF0FB;
    --text-muted: #93A1B7;
}

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}
h1,h2,h3{
    font-family:'Plus Jakarta Sans',sans-serif;
}
header, footer, #MainMenu{
    visibility:hidden;
}

/* ===================== FONDO DINÁMICO ===================== */
.stApp{
    background:
        radial-gradient(circle at 15% 20%, rgba(245,165,36,.18), transparent 30%),
        radial-gradient(circle at 85% 10%, rgba(45,212,191,.16), transparent 32%),
        radial-gradient(circle at 75% 90%, rgba(251,113,133,.10), transparent 30%),
        radial-gradient(circle at 20% 90%, rgba(45,212,191,.12), transparent 28%),
        radial-gradient(circle, rgba(255,255,255,.05) 1px, transparent 1.6px) 0 0/28px 28px,
        linear-gradient(135deg, #0B1220, #0F1A2E, #0B1220);
    background-size: 400% 400%, 400% 400%, 400% 400%, 400% 400%, 28px 28px, 400% 400%;
    animation: fondo 24s ease infinite;
}
@keyframes fondo{
    0%{background-position:0% 50%,0% 50%,0% 50%,0% 50%,0 0,0% 50%;}
    50%{background-position:100% 50%,100% 50%,100% 50%,100% 50%,14px 14px,100% 50%;}
    100%{background-position:0% 50%,0% 50%,0% 50%,0% 50%,0 0,0% 50%;}
}

.block-container{
    padding-top:1.2rem;
    padding-left:2rem;
    padding-right:2rem;
    max-width:1700px;
}

/* ===================== HERO ===================== */
.hero{
    padding:32px 25px;
    border-radius:28px;
    background: var(--glass-bg);
    backdrop-filter: blur(18px);
    border:1px solid var(--glass-border);
    text-align:center;
    margin-bottom:24px;
}
.logo-wrap{
    display:flex;
    justify-content:center;
    margin-bottom:8px;
    animation: flotar 4s ease-in-out infinite;
}
@keyframes flotar{
    0%{transform:translateY(0px);}
    50%{transform:translateY(-8px);}
    100%{transform:translateY(0px);}
}
.titulo{
    font-family:'Plus Jakarta Sans',sans-serif;
    font-size:44px;
    font-weight:800;
    letter-spacing:1px;
    background:linear-gradient(90deg,#F5A524,#2DD4BF,#F5A524);
    background-size:300% auto;
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
    animation:brillo 7s linear infinite;
}
@keyframes brillo{
    0%{background-position:0% center;}
    100%{background-position:300% center;}
}
.subtitulo{
    font-size:17px;
    color: var(--text-muted);
    margin-top:8px;
    max-width:600px;
    margin-left:auto;
    margin-right:auto;
}

/* ===================== TÍTULOS DE SECCIÓN ===================== */
.section{
    font-size:23px;
    font-weight:800;
    margin:30px 0 14px 0;
    color: var(--text-primary);
    display:flex;
    align-items:center;
    gap:10px;
}
.section::after{
    content:"";
    flex:1;
    height:1px;
    background:linear-gradient(90deg, rgba(245,165,36,.45), transparent);
    margin-left:10px;
}

/* ===================== CARDS DE MÉTRICAS / RESULTADOS ===================== */
.card{
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border:1px solid var(--glass-border);
    border-radius:20px;
    padding:22px 18px;
    min-height:190px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    box-shadow:0 15px 35px rgba(0,0,0,.25);
    transition:.3s;
}
.card:hover{
    transform:translateY(-6px);
    box-shadow:0 22px 45px rgba(0,0,0,.4);
    border-color: rgba(245,165,36,.4);
}
.icon-badge{
    width:52px;
    height:52px;
    border-radius:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
    margin-bottom:10px;
}
.badge-amber{ background:rgba(245,165,36,.15); }
.badge-teal{ background:rgba(45,212,191,.15); }
.badge-coral{ background:rgba(251,113,133,.15); }
.badge-slate{ background:rgba(148,163,184,.15); }

.metric-title{
    color: var(--text-muted);
    font-size:13px;
    text-transform:uppercase;
    letter-spacing:.5px;
}
.metric-value{
    font-size:30px;
    font-weight:800;
    color: var(--text-primary);
    margin-top:2px;
}
.metric-sub{
    color: var(--text-muted);
    font-size:13px;
    margin-top:2px;
}

/* ===================== CARDS DE PRODUCTOS (sticker) ===================== */
.stButton button{
    background: var(--glass-bg);
    backdrop-filter: blur(14px);
    border:1px solid var(--glass-border) !important;
    border-radius:18px;
    min-height:88px;
    width:100%;
    font-size:19px !important;
    font-weight:700 !important;
    color: var(--text-primary) !important;
    transition:.25s;
    white-space:normal;
    line-height:1.4;
}
.stButton button:hover{
    transform:translateY(-5px);
    border-color: var(--accent-amber) !important;
    color: var(--accent-amber) !important;
    box-shadow:0 15px 30px rgba(0,0,0,.35);
}

/* ===================== BOTÓN PRINCIPAL (buscar) ===================== */
div[data-testid="stFormSubmitButton"] button{
    background: linear-gradient(90deg, var(--accent-amber), var(--accent-teal));
    border:none;
    border-radius:14px;
    height:52px;
    font-weight:800;
    font-size:16px;
    color:#0B1220;
    transition:.3s;
    letter-spacing:.3px;
}
div[data-testid="stFormSubmitButton"] button:hover{
    transform:scale(1.02);
    box-shadow:0 14px 30px rgba(245,165,36,.35);
}

/* ===================== INPUTS ===================== */
.stTextInput input, .stNumberInput input{
    background: var(--panel-bg) !important;
    color: var(--text-primary) !important;
    border-radius:12px !important;
    border:1px solid var(--glass-border) !important;
}
.stTextInput input:focus, .stNumberInput input:focus{
    border-color: var(--accent-amber) !important;
    box-shadow:0 0 0 3px rgba(245,165,36,.25) !important;
}
div[data-baseweb="select"] > div{
    background: var(--panel-bg) !important;
    border-radius:12px !important;
    border:1px solid var(--glass-border) !important;
}

div[data-testid="stForm"]{
    background: rgba(255,255,255,.05);
    padding:22px;
    border-radius:22px;
    border:1px solid var(--glass-border);
}

/* ===================== TABLAS Y ALERTAS ===================== */
div[data-testid="stDataFrame"]{
    border-radius:16px;
    overflow:hidden;
    border:1px solid var(--glass-border);
}
div[data-testid="stAlert"]{
    border-radius:16px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# HERO
# ==========================================

st.markdown("""
<div class="hero">
    <div class="logo-wrap">
        <svg width="66" height="80" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="pinGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#F5A524"/>
                    <stop offset="100%" stop-color="#2DD4BF"/>
                </linearGradient>
            </defs>
            <path d="M50 3 C25 3 5 23 5 48 C5 76 50 116 50 116 C50 116 95 76 95 48 C95 23 75 3 50 3 Z" fill="url(#pinGrad)"/>
            <circle cx="50" cy="47" r="29" fill="#0B1220"/>
            <text x="50" y="58" font-size="32" font-weight="800" fill="#F5A524" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif">$</text>
        </svg>
    </div>
    <div class="titulo">MAPLAB</div>
    <div class="subtitulo">
        Compara precios entre supermercados cercanos y descubre dónde comprar más barato.
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# ESTADO DE SESIÓN
# ==========================================

st.session_state.setdefault("nombre_input", "")
st.session_state.setdefault("resultado", None)
st.session_state.setdefault("error_msg", None)
st.session_state.setdefault("lat_buscada", LAT_REFERENCIA)
st.session_state.setdefault("lon_buscada", LON_REFERENCIA)

# ==========================================
# PRODUCTOS DISPONIBLES (cards tipo sticker, mismo tamaño)
# ==========================================

productos = obtener_productos()

if productos:
    st.markdown('<div class="section">🛍️ Productos disponibles</div>', unsafe_allow_html=True)

    nombres = []
    for p in productos:
        nombre = p.get("nombre")
        if nombre and nombre not in nombres:
            nombres.append(nombre)
    nombres = nombres[:8]

    columnas = st.columns(4, gap="medium")
    for i, nombre in enumerate(nombres):
        icono = obtener_icono(nombre)
        with columnas[i % 4]:
            if st.button(f"{icono}  {nombre}", use_container_width=True, key=f"producto_{i}"):
                st.session_state.nombre_input = nombre
                st.rerun()

# ==========================================
# FORMULARIO DE BÚSQUEDA
# ==========================================

st.markdown('<div class="section">🔎 Buscar producto</div>', unsafe_allow_html=True)

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

    st.info("📍 Puedes usar las coordenadas por defecto o ingresar tu ubicación.")

    buscar = st.form_submit_button("🔍 Buscar mejores precios", use_container_width=True)

# ==========================================
# CONSULTA A LA API
# ==========================================

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

# ==========================================
# RESULTADOS
# ==========================================

resultado = st.session_state.resultado
error_msg = st.session_state.error_msg

if resultado is None and error_msg is None:

    # Estado vacío: en vez de dejar la pantalla en blanco, guiamos al usuario
    st.markdown('<div class="section">✨ Cómo funciona</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3, gap="medium")
    pasos = [
        (p1, "badge-teal", "🔎", "1. Busca", "Escribe un producto o elige uno de la lista de arriba."),
        (p2, "badge-amber", "📊", "2. Compara", "Revisa precios y distancias de las tiendas cercanas."),
        (p3, "badge-coral", "💰", "3. Ahorra", "Elige la mejor opción entre precio y cercanía."),
    ]
    for col, badge, icono, titulo_paso, texto in pasos:
        with col:
            st.markdown(f"""
            <div class="card" style="min-height:170px;">
                <div class="icon-badge {badge}">{icono}</div>
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

        icono = obtener_icono(resultado["producto_nombre"])

        st.markdown(
            f'<div class="section">{icono} Resultado para: {resultado["producto_nombre"]}</div>',
            unsafe_allow_html=True,
        )
        if resultado.get("marca"):
            st.caption(f"Marca: **{resultado['marca']}**")

        # -------- 4 cards de métricas, mismo tamaño --------
        c1, c2, c3, c4 = st.columns(4, gap="medium")

        with c1:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-amber">🏆</div>
                <div class="metric-title">Precio más bajo</div>
                <div class="metric-value">${mejor['precio']:.2f}</div>
                <div class="metric-sub">{mejor['tienda_nombre']}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-teal">📍</div>
                <div class="metric-title">Tienda más cercana</div>
                <div class="metric-value">{cercano['distancia_km']:.2f} km</div>
                <div class="metric-sub">{cercano['tienda_nombre']}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-coral">🏷️</div>
                <div class="metric-title">Ahorro potencial</div>
                <div class="metric-value">${ahorro:.2f}</div>
                <div class="metric-sub">{ahorro_pct:.0f}% vs. el más caro</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="card">
                <div class="icon-badge badge-slate">🏪</div>
                <div class="metric-title">Tiendas comparadas</div>
                <div class="metric-value">{len(df)}</div>
                <div class="metric-sub">en la zona</div>
            </div>
            """, unsafe_allow_html=True)

        # -------- Gráficas --------
        st.markdown('<div class="section">📊 Comparación visual</div>', unsafe_allow_html=True)
        izquierda, derecha = st.columns([1.1, 1], gap="medium")

        with izquierda:
            df_sorted = df.sort_values("precio", ascending=True)
            colores_barras = [
                COLOR_AMBER if p == precio_min else COLOR_BAR_MUTED for p in df_sorted["precio"]
            ]
            fig = px.bar(
                df_sorted,
                x="precio",
                y="tienda_nombre",
                orientation="h",
                text="precio",
                title="Ranking de precios",
            )
            fig.update_traces(
                marker_color=colores_barras,
                texttemplate="$%{text:.2f}",
                textposition="outside",
                textfont=dict(color=COLOR_TEXT),
            )
            fig.update_yaxes(autorange="reversed", title="")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=COLOR_TEXT, family="Inter"),
                title_font=dict(color=COLOR_TEXT, size=16),
                height=380,
                xaxis_title="Precio ($)",
                margin=dict(l=10, r=10, t=50, b=10),
            )
            fig.update_xaxes(gridcolor="rgba(255,255,255,.08)")
            st.plotly_chart(fig, use_container_width=True)

        with derecha:
            dist_med = df["distancia_km"].median()
            precio_med = df["precio"].median()

            fig2 = px.scatter(
                df,
                x="distancia_km",
                y="precio",
                text="tienda_nombre",
                title="Precio vs. distancia",
            )
            fig2.update_traces(
                mode="markers+text",
                textposition="top center",
                textfont=dict(color=COLOR_MUTED, size=11),
                marker=dict(size=15, color=COLOR_TEAL, line=dict(width=2, color=COLOR_BG)),
            )
            fig2.add_shape(
                type="rect",
                x0=0, x1=dist_med, y0=0, y1=precio_med,
                fillcolor=COLOR_AMBER, opacity=0.08, line_width=0, layer="below",
            )
            fig2.add_annotation(
                x=dist_med / 2 if dist_med > 0 else 0,
                y=precio_med / 2 if precio_med > 0 else 0,
                text="Zona ideal 🎯",
                showarrow=False,
                font=dict(color=COLOR_AMBER, size=12),
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=COLOR_TEXT, family="Inter"),
                title_font=dict(color=COLOR_TEXT, size=16),
                height=380,
                xaxis_title="Distancia (km)",
                yaxis_title="Precio ($)",
                showlegend=False,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            fig2.update_xaxes(gridcolor="rgba(255,255,255,.08)")
            fig2.update_yaxes(gridcolor="rgba(255,255,255,.08)")
            st.plotly_chart(fig2, use_container_width=True)

        # -------- Tabla comparativa --------
        st.markdown('<div class="section">📋 Tabla comparativa</div>', unsafe_allow_html=True)

        mostrar = df[["tienda_nombre", "direccion", "precio", "distancia_km"]].sort_values("precio").reset_index(drop=True)

        puestos = []
        for i in range(len(mostrar)):
            if i == 0:
                puestos.append("🥇")
            elif i == 1:
                puestos.append("🥈")
            elif i == 2:
                puestos.append("🥉")
            else:
                puestos.append(f"#{i + 1}")
        mostrar.insert(0, "Puesto", puestos)

        mostrar = mostrar.rename(columns={
            "tienda_nombre": "Supermercado",
            "direccion": "Dirección",
            "precio": "Precio",
            "distancia_km": "Distancia",
        })

        st.dataframe(
            mostrar,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Puesto": st.column_config.TextColumn("Puesto", width="small"),
                "Supermercado": st.column_config.TextColumn("Supermercado"),
                "Dirección": st.column_config.TextColumn("Dirección"),
                "Precio": st.column_config.ProgressColumn(
                    "Precio", format="$%.2f", min_value=0, max_value=float(precio_max) * 1.05
                ),
                "Distancia": st.column_config.NumberColumn("Distancia", format="%.2f km"),
            },
        )

        st.caption(
            f"Precio promedio: **${df['precio'].mean():.2f}**  •  "
            f"Distancia promedio: **{df['distancia_km'].mean():.2f} km**"
        )

        # -------- Mapa --------
        st.markdown('<div class="section">🗺️ Ubicación de referencia</div>', unsafe_allow_html=True)
        st.map(
            pd.DataFrame([{
                "lat": st.session_state.lat_buscada,
                "lon": st.session_state.lon_buscada,
            }]),
            size=300,
            zoom=15,
        )

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:20px;opacity:.7;">
    <h4>🛒 MAPLAB</h4>
    <p>Comparador Inteligente de Precios</p>
    <p>Desarrollado con ❤️ usando Streamlit + FastAPI</p>
</div>
""", unsafe_allow_html=True)
