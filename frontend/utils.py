# frontend/utils.py
import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Punto de referencia entre las dos tiendas de prueba sembradas por seed.py
# (Súper Xtra David y Super 99 David) — el mismo que usa API_DOCS.md.
LAT_REFERENCIA = 8.4283
LON_REFERENCIA = -82.4400


@st.cache_data(ttl=60)
def obtener_productos():
    """
    GET /productos — lista de productos disponibles, para armar sugerencias
    de búsqueda. Si el backend no responde, devuelve una lista vacía en vez
    de romper la pantalla (las sugerencias simplemente no se muestran).
    """
    try:
        resp = requests.get(f"{API_BASE_URL}/productos", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException:
        pass
    return []


def comparar_producto(nombre: str, lat: float, lon: float, limite: int = 2, timeout: int = 10):
    """
    GET /productos/comparar — RF1 (buscar por nombre) + RF2 (comparar por
    ubicación) en una sola llamada.

    Devuelve una tupla (datos, error):
      - (dict_respuesta, None) -> éxito. dict_respuesta trae
        producto_id, producto_nombre, marca y precios (lista ya ordenada
        por distancia, según define el backend).
      - (None, "mensaje")      -> sin resultados (404) o error de conexión/servidor.
        El "mensaje" en el caso 404 es el mismo `detail` que arma el backend,
        pensado para mostrarse tal cual al usuario.
    """
    try:
        resp = requests.get(
            f"{API_BASE_URL}/productos/comparar",
            params={"nombre": nombre, "lat": lat, "lon": lon, "limite": limite},
            timeout=timeout,
        )
    except requests.exceptions.ConnectionError:
        return None, "No se pudo conectar con el servidor. Verifica que el backend esté corriendo (uvicorn backend.main:app --reload)."
    except requests.exceptions.Timeout:
        return None, "El servidor tardó demasiado en responder. Intenta de nuevo."
    except requests.exceptions.RequestException as e:
        return None, f"Ocurrió un error al conectar con el servidor: {e}"

    if resp.status_code == 200:
        return resp.json(), None
    elif resp.status_code == 404:
        try:
            detalle = resp.json().get("detail", "No se encontraron resultados.")
        except ValueError:
            detalle = "No se encontraron resultados."
        return None, detalle
    elif resp.status_code == 422:
        return None, "Parámetros inválidos: revisa el nombre del producto y las coordenadas."
    else:
        return None, f"Error inesperado del servidor (código {resp.status_code})."
