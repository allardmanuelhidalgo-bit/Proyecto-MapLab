import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import (
    obtener_productos,
    comparar_producto,
    LAT_REFERENCIA,
    LON_REFERENCIA,
)

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="MapLab",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# ICONOS DE PRODUCTOS
# ==========================================

PRODUCTOS_ICONOS = {
    "leche":"🥛",
    "arroz":"🍚",
    "queso":"🧀",
    "cafe":"☕",
    "café":"☕",
    "aceite":"🛢️",
    "azucar":"🍬",
    "azúcar":"🍬",
    "detergente":"🧴",
    "jabon":"🧼",
    "jabón":"🧼",
    "pollo":"🍗",
    "huevo":"🥚",
    "atun":"🐟",
    "atún":"🐟",
    "pan":"🍞",
    "agua":"💧",
    "gaseosa":"🥤",
    "sal":"🧂",
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

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

html,body,[class*="css"]{

font-family:'Inter',sans-serif;

}

h1,h2,h3{

font-family:'Plus Jakarta Sans',sans-serif;

}

header,footer,#MainMenu{

visibility:hidden;

}

/* ================================= */

.stApp{

background:

radial-gradient(circle at 20% 20%,rgba(59,130,246,.25),transparent 25%),

radial-gradient(circle at 80% 0%,rgba(16,185,129,.20),transparent 30%),

radial-gradient(circle at 80% 80%,rgba(99,102,241,.20),transparent 30%),

linear-gradient(135deg,#0F172A,#111827,#0F172A);

background-size:400% 400%;

animation:fondo 18s ease infinite;

}

/* ================================= */

@keyframes fondo{

0%{

background-position:0% 50%;

}

50%{

background-position:100% 50%;

}

100%{

background-position:0% 50%;

}

}

/* ================================= */

.block-container{

padding-top:.5rem;
padding-left:2rem;
padding-right:2rem;
max-width:1700px;

}

/* ================================= */

.hero{

padding:25px;

border-radius:25px;

background:rgba(255,255,255,.08);

backdrop-filter:blur(18px);

border:1px solid rgba(255,255,255,.08);

text-align:center;

margin-bottom:25px;

}

/* ================================= */

.logo{

font-size:70px;

margin-bottom:10px;

animation:flotar 4s ease infinite;

}

@keyframes flotar{

0%{

transform:translateY(0px);

}

50%{

transform:translateY(-8px);

}

100%{

transform:translateY(0px);

}

}

/* ================================= */

.titulo{

@keyframes gradient{

0%{

background-position:0%;

}

100%{

background-position:300%;

}

background:linear-gradient(90deg,#2563EB,#10B981,#FACC15,#2563EB);

.subtitulo{

font-size:20px;

color:#E2E8F0;

}

/* ================================= */

.card{

background:rgba(255,255,255,.10);

backdrop-filter:blur(20px);

border:1px solid rgba(255,255,255,.15);

border-radius:22px;

padding:25px;

height:180px;

display:flex;

flex-direction:column;

justify-content:center;

box-shadow:0 15px 35px rgba(0,0,0,.25);

transition:.3s;

}

.card:hover{

transform:translateY(-8px);

box-shadow:0 25px 45px rgba(0,0,0,.45);

border:1px solid #60A5FA;

}

/* ================================= */

.metric-title{

color:#CBD5E1;

font-size:14px;

text-transform:uppercase;

}

.metric-value{

font-size:34px;

font-weight:800;

color:white;

}

.metric-sub{

color:#94A3B8;

}

/* ================================= */

.stTextInput input{

background:#1E293B !important;

color:white !important;

border-radius:12px;

}

.stNumberInput input{

background:#1E293B !important;

color:white !important;

border-radius:12px;

}

.stButton button{

background:linear-gradient(90deg,#2563EB,#10B981);

border:none;

border-radius:14px;

height:50px;

font-weight:700;

font-size:16px;

color:white;

transition:.3s;

}

.stButton button:hover{

transform:scale(1.03);

}

/* ================================= */

div[data-testid="stForm"]{

background:rgba(255,255,255,.06);

padding:20px;

border-radius:20px;

border:1px solid rgba(255,255,255,.08);

}

/* ================================= */

table{

border-radius:15px;

overflow:hidden;

}

/* ================================= */

.section{

font-size:28px;

font-weight:700;

margin-top:20px;

margin-bottom:15px;

color:white;

}

</style>

""",unsafe_allow_html=True)

# ==========================================
# HERO
# ==========================================

st.markdown("""

<div class="hero">

<div class="logo">

🗺️💲

</div>

<div class="titulo">

MAPLAB

</div>

<div class="subtitulo">

Compara precios entre supermercados cercanos y descubre dónde comprar más barato.

</div>

</div>

""",unsafe_allow_html=True)

# ==========================================
# ESTADO DE SESIÓN
# ==========================================

st.session_state.setdefault("nombre_input", "")
st.session_state.setdefault("resultado", None)
st.session_state.setdefault("error_msg", None)
st.session_state.setdefault("lat_buscada", LAT_REFERENCIA)
st.session_state.setdefault("lon_buscada", LON_REFERENCIA)

# ==========================================
# PRODUCTOS DISPONIBLES
# ==========================================

productos = obtener_productos()

if productos:

    st.markdown(
        '<div class="section">🛍️ Productos disponibles</div>',
        unsafe_allow_html=True
    )

    nombres = []

    for p in productos:

        nombre = p.get("nombre")

        if nombre and nombre not in nombres:

            nombres.append(nombre)

    nombres = nombres[:8]

    columnas = st.columns(4)

    for i, nombre in enumerate(nombres):

        icono = obtener_icono(nombre)

        with columnas[i % 4]:

            if st.button(
                f"{icono} {nombre}",
                use_container_width=True,
                key=f"producto_{i}"
            ):

                st.session_state.nombre_input = nombre
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# FORMULARIO
# ==========================================

st.markdown(
    '<div class="section">🔎 Buscar producto</div>',
    unsafe_allow_html=True
)

with st.form("buscar_producto"):

    c1, c2 = st.columns([3,1])

    with c1:

        nombre_producto = st.text_input(
            "Producto",
            placeholder="Ejemplo: Leche, Arroz, Aceite...",
            key="nombre_input"
        )

    with c2:

        limite = st.selectbox(
            "Tiendas",
            [2,3,4,5,6,7,8],
            index=0
        )

    c3, c4 = st.columns(2)

    with c3:

        lat = st.number_input(
            "Latitud",
            value=LAT_REFERENCIA,
            format="%.6f"
        )

    with c4:

        lon = st.number_input(
            "Longitud",
            value=LON_REFERENCIA,
            format="%.6f"
        )

    st.info(
        "📍 Puedes usar las coordenadas por defecto o ingresar tu ubicación."
    )

    buscar = st.form_submit_button(
        "🔍 Buscar mejores precios",
        use_container_width=True
    )

# ==========================================
# CONSULTA API
# ==========================================

if buscar:

    if nombre_producto.strip() == "":

        st.warning("Debes escribir un producto.")

    else:

        with st.spinner("Buscando supermercados cercanos..."):

            datos, error = comparar_producto(

                nombre_producto.strip(),

                lat,

                lon,

                limite=limite

            )

        st.session_state.resultado = datos

        st.session_state.error_msg = error

        st.session_state.lat_buscada = lat

        st.session_state.lon_buscada = lon

# ------------------------------------------------------------------
# RESULTADOS
# ------------------------------------------------------------------
# ==========================================
# RESULTADOS
# ==========================================

resultado = st.session_state.resultado
error_msg = st.session_state.error_msg

if resultado is None and error_msg is None:

    st.info("👆 Busca un producto para comenzar.")

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

        icono = obtener_icono(resultado["producto_nombre"])

        st.markdown("---")

        st.markdown(
            f"""
            <div class="section">
            {icono} Resultado para: <b>{resultado['producto_nombre']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        if resultado.get("marca"):

            st.caption(f"Marca: **{resultado['marca']}**")

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown(f"""
            <div class="card">
            <div style="font-size:45px;">🏆</div>

            <div class="metric-title">
            Precio más bajo
            </div>

            <div class="metric-value">
            ${mejor['precio']:.2f}
            </div>

            <div class="metric-sub">
            {mejor['tienda_nombre']}
            </div>

            </div>
            """, unsafe_allow_html=True)

        with c2:

            st.markdown(f"""
            <div class="card">
            <div style="font-size:45px;">📍</div>

            <div class="metric-title">
            Tienda más cercana
            </div>

            <div class="metric-value">
            {cercano['distancia_km']:.2f} km
            </div>

            <div class="metric-sub">
            {cercano['tienda_nombre']}
            </div>

            </div>
            """, unsafe_allow_html=True)

        with c3:

            st.markdown(f"""
            <div class="card">
            <div style="font-size:45px;">🏬</div>

            <div class="metric-title">
            Tiendas
            </div>

            <div class="metric-value">
            {len(df)}
            </div>

            <div class="metric-sub">
            Comparadas
            </div>

            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        izquierda, derecha = st.columns([1.2,1])

        with izquierda:

            fig = px.bar(
                df.sort_values("precio"),
                x="tienda_nombre",
                y="precio",
                text="precio",
                title="💲 Comparación de precios"
            )

            fig.update_traces(texttemplate="$%{text:.2f}")

            fig.update_layout(
                template="plotly_dark",
                height=380,
                xaxis_title="",
                yaxis_title="Precio ($)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with derecha:

            fig2 = px.pie(
                df,
                names="tienda_nombre",
                values="precio",
                hole=.60,
                title="Distribución de precios"
            )

            fig2.update_layout(
                template="plotly_dark",
                height=380
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        izquierda, derecha = st.columns([2,1])

        with izquierda:

            mostrar = df.copy()

            mostrar = mostrar.rename(columns={

                "tienda_nombre":"Supermercado",

                "direccion":"Dirección",

                "precio":"Precio",

                "distancia_km":"Distancia (km)"

            })

            mostrar = mostrar.sort_values("Precio")

            mostrar["Precio"] = mostrar["Precio"].map(
                lambda x:f"${x:.2f}"
            )

            mostrar["Distancia (km)"] = mostrar[
                "Distancia (km)"
            ].map(
                lambda x:f"{x:.2f}"
            )

            st.dataframe(

                mostrar,

                use_container_width=True,

                hide_index=True

            )

        with derecha:

            fig3 = px.bar(

                df.sort_values("distancia_km"),

                x="tienda_nombre",

                y="distancia_km",

                text="distancia_km",

                title="📍 Distancia"

            )

            fig3.update_layout(

                template="plotly_dark",

                height=350,

                xaxis_title="",

                yaxis_title="Kilómetros"

            )

            st.plotly_chart(

                fig3,

                use_container_width=True

            )

        st.markdown("---")

        st.subheader("📈 Ranking de supermercados")

        ranking = df.sort_values(
            "precio"
        ).reset_index(drop=True)

        for i, fila in ranking.iterrows():

            if i == 0:

                emoji = "🥇"

            elif i == 1:

                emoji = "🥈"

            elif i == 2:

                emoji = "🥉"

            else:

                emoji = "🏪"

            st.success(

                f"{emoji} **{fila['tienda_nombre']}**  •  "
                f"${fila['precio']:.2f}  •  "
                f"{fila['distancia_km']:.2f} km"

            )

        st.markdown("---")

        st.markdown("---")

        c1,c2,c3,c4=st.columns(4)

        c1.metric(
            "Precio promedio",
            f"${df['precio'].mean():.2f}"
        )

        c2.metric(
            "Precio mínimo",
            f"${df['precio'].min():.2f}"
        )

        c3.metric(
            "Precio máximo",
            f"${df['precio'].max():.2f}"
        )

        c4.metric(
            "Distancia promedio",
            f"{df['distancia_km'].mean():.2f} km"
        )

        st.map(
    pd.DataFrame([{
        "lat":st.session_state.lat_buscada,
        "lon":st.session_state.lon_buscada
    }]),
    size=300,
    zoom=15
)

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.markdown("---")

st.markdown(
"""
<div style="text-align:center;padding:20px;opacity:.7;">
<h4>🛒 MAPLAB</h4>
<p>Comparador Inteligente de Precios</p>
<p>Desarrollado con ❤️ usando Streamlit + FastAPI</p>
</div>
""",
unsafe_allow_html=True
)