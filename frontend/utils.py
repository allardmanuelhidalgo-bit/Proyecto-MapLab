# frontend/utils.py
"""
Funciones de apoyo para el frontend de MapLab.

Incluye:
- La URL del backend (configurable por variable de entorno).
- Geolocalización del usuario (vía JS del navegador, cacheada en session_state).
- Identificación simple de usuario (sin contraseña) para poder votar/reportar/listar.
- Wrappers de cada endpoint del backend que el frontend necesita consumir.
"""

import os
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Datos de ejemplo (respaldo si el backend/base de datos todavía no responden)
TIENDAS_EJEMPLO = pd.DataFrame([
    {
        "nombre": "Súper Xtra David",
        "direccion": "Urbanización Brisas Davideñas, David, Chiriquí",
        "lat": 8.4283,
        "lon": -82.4400,
    },
    {
        "nombre": "Super 99 David",
        "direccion": "Calle F Sur, San Mateo, David, Chiriquí",
        "lat": 8.4310,
        "lon": -82.4370,
    },
])

# Coordenadas de respaldo si el usuario no da permiso de ubicación
UBICACION_RESPALDO = {"lat": 8.4283, "lon": -82.4400}  # David, Chiriquí


# ---------------------------------------------------------------------
# TIENDAS
# ---------------------------------------------------------------------

def obtener_tiendas() -> pd.DataFrame:
    """DataFrame con columnas lat/lon/nombre/direccion para el mapa."""
    try:
        resp = requests.get(f"{BACKEND_URL}/tiendas", timeout=3)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return TIENDAS_EJEMPLO

        df = pd.DataFrame(data)
        df = df.rename(columns={"latitud": "lat", "longitud": "lon"})
        return df[["nombre", "direccion", "lat", "lon"]]

    except Exception:
        return TIENDAS_EJEMPLO


def backend_esta_disponible() -> bool:
    try:
        requests.get(f"{BACKEND_URL}/productos", timeout=2)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------
# GEOLOCALIZACIÓN DEL USUARIO
# ---------------------------------------------------------------------
# Streamlit no tiene geolocalización nativa. Truco: un componente HTML
# invisible le pide al navegador la ubicación (navigator.geolocation) y,
# si la consigue, la agrega como query params (?lat=..&lon=..) a la URL
# de la página. Streamlit los puede leer con st.query_params. Una vez
# leídos, los guardamos en session_state para no repetir el permiso en
# cada página.

def solicitar_ubicacion_navegador():
    """Dispara el pedido de geolocalización del navegador (silencioso)."""
    components.html(
        """
        <script>
        navigator.geolocation.getCurrentPosition(
            function(pos) {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const params = new URLSearchParams(window.top.location.search);
                if (params.get("lat") !== String(lat)) {
                    params.set("lat", lat);
                    params.set("lon", lon);
                    window.top.location.search = params.toString();
                }
            },
            function(err) {
                console.log("Geolocalización no disponible:", err.message);
            }
        );
        </script>
        """,
        height=0,
    )


def obtener_ubicacion_usuario(pedir_si_falta: bool = True) -> dict:
    """
    Devuelve {"lat": float, "lon": float} de la ubicación real del usuario.

    Orden de búsqueda:
    1. session_state (ya la pedimos antes en esta sesión)
    2. query params de la URL (el navegador ya respondió)
    3. dispara el pedido al navegador y muestra un aviso mientras tanto
       (usa UBICACION_RESPALDO hasta que el usuario acepte el permiso)
    """
    if "user_lat" in st.session_state and "user_lon" in st.session_state:
        return {"lat": st.session_state["user_lat"], "lon": st.session_state["user_lon"]}

    query_lat = st.query_params.get("lat")
    query_lon = st.query_params.get("lon")
    if query_lat is not None and query_lon is not None:
        st.session_state["user_lat"] = float(query_lat)
        st.session_state["user_lon"] = float(query_lon)
        return {"lat": st.session_state["user_lat"], "lon": st.session_state["user_lon"]}

    if pedir_si_falta:
        solicitar_ubicacion_navegador()

    return dict(UBICACION_RESPALDO)


def ubicacion_es_real() -> bool:
    """True si ya tenemos la ubicación real del navegador (no el respaldo)."""
    return "user_lat" in st.session_state and "user_lon" in st.session_state


# ---------------------------------------------------------------------
# USUARIO (sin contraseña, solo nombre + email)
# ---------------------------------------------------------------------

def usuario_actual() -> dict | None:
    return st.session_state.get("usuario")


def identificarse(nombre: str, email: str) -> tuple[bool, str]:
    """
    Crea el usuario en el backend (POST /usuarios) y lo guarda en
    session_state. Como el backend no tiene login/GET-por-email, si el
    email ya existe no hay forma de recuperar su id: se lo decimos al
    usuario en vez de fallar en silencio.
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}/usuarios",
            json={"nombre": nombre, "email": email},
            timeout=5,
        )
        if resp.status_code == 201:
            st.session_state["usuario"] = resp.json()
            return True, "Listo."
        if resp.status_code == 400:
            return False, (
                "Ese email ya está registrado de una sesión anterior. "
                "El backend todavía no tiene un endpoint para 'iniciar sesión' "
                "con un email existente (solo crear uno nuevo), así que por ahora "
                "usa otro email para identificarte."
            )
        return False, f"Error inesperado ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"No se pudo conectar con el backend: {e}"


def cerrar_sesion():
    st.session_state.pop("usuario", None)


# ---------------------------------------------------------------------
# PRODUCTOS
# ---------------------------------------------------------------------

def listar_categorias() -> list[dict]:
    try:
        resp = requests.get(f"{BACKEND_URL}/categorias", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def crear_producto(nombre: str, categoria_id: int, marca: str | None = None) -> tuple[bool, dict | str]:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/productos",
            json={"nombre": nombre, "categoria_id": categoria_id, "marca": marca},
            timeout=5,
        )
        if resp.status_code == 201:
            return True, resp.json()
        return False, resp.json().get("detail", resp.text)
    except Exception as e:
        return False, str(e)


def comparar_producto(nombre: str, lat: float, lon: float, limite: int = 5) -> tuple[bool, dict | str]:
    """Llama a GET /productos/comparar (RF1 + RF2)."""
    try:
        resp = requests.get(
            f"{BACKEND_URL}/productos/comparar",
            params={"nombre": nombre, "lat": lat, "lon": lon, "limite": limite},
            timeout=8,
        )
        if resp.status_code == 200:
            return True, resp.json()
        return False, resp.json().get("detail", resp.text)
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------
# TIENDAS (crear)
# ---------------------------------------------------------------------

def crear_tienda(nombre: str, direccion: str, lat: float, lon: float) -> tuple[bool, dict | str]:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/tiendas",
            json={"nombre": nombre, "direccion": direccion, "latitud": lat, "longitud": lon},
            timeout=5,
        )
        if resp.status_code == 201:
            return True, resp.json()
        return False, resp.json().get("detail", resp.text)
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------
# PRECIOS Y VOTOS
# ---------------------------------------------------------------------

def registrar_precio(producto_id: int, tienda_id: int, precio: float, usuario_id: int | None) -> tuple[bool, dict | str]:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/precios",
            json={
                "producto_id": producto_id,
                "tienda_id": tienda_id,
                "precio": precio,
                "usuario_id": usuario_id,
            },
            timeout=5,
        )
        if resp.status_code == 201:
            return True, resp.json()
        return False, resp.json().get("detail", resp.text)
    except Exception as e:
        return False, str(e)


def votar_precio(precio_id: int, usuario_id: int, es_verdadero: bool) -> tuple[bool, str]:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/precios/{precio_id}/votar",
            json={"usuario_id": usuario_id, "es_verdadero": es_verdadero},
            timeout=5,
        )
        if resp.status_code == 201:
            return True, "¡Gracias por tu voto!"
        return False, resp.json().get("detail", resp.text)
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------
# LISTA PERSONAL
# ---------------------------------------------------------------------

def obtener_lista(usuario_id: int) -> list[dict]:
    try:
        resp = requests.get(f"{BACKEND_URL}/listas/{usuario_id}", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def agregar_a_lista(usuario_id: int, producto_id: int) -> tuple[bool, str]:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/listas",
            json={"usuario_id": usuario_id, "producto_id": producto_id},
            timeout=5,
        )
        if resp.status_code == 201:
            return True, "Agregado a tu lista."
        return False, resp.json().get("detail", resp.text)
    except Exception as e:
        return False, str(e)


def marcar_comprado(item_id: int, comprado: bool) -> bool:
    try:
        resp = requests.patch(
            f"{BACKEND_URL}/listas/{item_id}",
            json={"comprado": comprado},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False


def quitar_de_lista(item_id: int) -> bool:
    try:
        resp = requests.delete(f"{BACKEND_URL}/listas/{item_id}", timeout=5)
        return resp.status_code == 204
    except Exception:
        return False

# ---------------------------------------------------------------------
# RUTAS (OSRM - motor de ruteo gratuito, sin API key)
# ---------------------------------------------------------------------
# Servidor demo público de OSRM. Gratis, sin key, pero con uso limitado
# (no comercial, ~1 req/seg). Si esto pasa a producción real, hay que
# montar un OSRM propio (Docker) o usar Mapbox/Google Directions.

OSRM_URL = os.getenv("OSRM_URL", "https://router.project-osrm.org")

_PERFILES_OSRM = {
    "carro": "driving",
    "a_pie": "foot",
    "bici": "bike",
}

# Traducción básica de las instrucciones que da OSRM (en inglés) a
# texto en español. No cubre el 100% de los casos, pero sí los típicos.
_TRADUCCION_MANIOBRAS = {
    "depart": "Sal por",
    "arrive": "Llegaste a tu destino",
    "turn-left": "Gira a la izquierda en",
    "turn-right": "Gira a la derecha en",
    "turn-straight": "Sigue derecho por",
    "turn-slight left": "Gira levemente a la izquierda en",
    "turn-slight right": "Gira levemente a la derecha en",
    "turn-sharp left": "Gira fuerte a la izquierda en",
    "turn-sharp right": "Gira fuerte a la derecha en",
    "turn-uturn": "Da vuelta en U en",
    "roundabout": "Toma la rotonda hacia",
    "new name": "Continúa por",
    "merge": "Incorpórate a",
    "fork": "Toma el desvío hacia",
}


def _texto_paso(paso: dict) -> str:
    maniobra = paso.get("maneuver", {})
    tipo = maniobra.get("type", "")
    modificador = maniobra.get("modifier", "")
    clave = f"{tipo}-{modificador}" if modificador else tipo
    base = _TRADUCCION_MANIOBRAS.get(clave, _TRADUCCION_MANIOBRAS.get(tipo, "Continúa por"))
    calle = paso.get("name") or ""
    return f"{base} {calle}".strip() if calle else base


def calcular_ruta(origen: dict, destino: dict, perfil: str = "carro") -> dict | None:
    """
    origen/destino: {"lat": float, "lon": float}
    perfil: "carro" | "a_pie" | "bici"

    Devuelve:
        {
            "distancia_km": float,
            "duracion_min": float,
            "puntos": [[lat, lon], ...],   # para dibujar la línea de la ruta
            "pasos": ["Sal por Calle X", "Gira a la derecha en...", ...],
        }
    o None si no se pudo calcular (sin internet, servidor caído, etc.)
    """
    perfil_osrm = _PERFILES_OSRM.get(perfil, "driving")
    coords = f"{origen['lon']},{origen['lat']};{destino['lon']},{destino['lat']}"
    url = f"{OSRM_URL}/route/v1/{perfil_osrm}/{coords}"

    try:
        resp = requests.get(
            url,
            params={"overview": "full", "geometries": "geojson", "steps": "true"},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            return None

        ruta = data["routes"][0]

        # geojson viene como [lon, lat]; folium quiere [lat, lon]
        puntos = [[lat, lon] for lon, lat in ruta["geometry"]["coordinates"]]

        pasos = []
        for leg in ruta.get("legs", []):
            for paso in leg.get("steps", []):
                pasos.append(_texto_paso(paso))

        return {
            "distancia_km": round(ruta["distance"] / 1000, 2),
            "duracion_min": round(ruta["duration"] / 60, 1),
            "puntos": puntos,
            "pasos": pasos,
        }
    except Exception:
        return None