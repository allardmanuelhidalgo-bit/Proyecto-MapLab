# Archivo base para frontend/utils.py
# frontend/utils.py
"""
Funciones de apoyo para el frontend de MapLab.

Por ahora incluye:
- La URL del backend (configurable por variable de entorno).
- Una función para traer las tiendas a mostrar en el mapa, con datos de
  ejemplo como respaldo si el backend todavía no está corriendo o si
  todavía no existe un endpoint /tiendas (solo existen /productos y
  /productos/comparar por ahora).
"""

import os
import pandas as pd
import requests

# URL base del backend FastAPI. Se puede sobreescribir con la variable de
# entorno BACKEND_URL (por ejemplo al desplegar en otro servidor).
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Datos de ejemplo (los mismos que aparecen en API_DOCS.md) para poder ver
# el mapa funcionando aunque el backend/la base de datos no estén listos.
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


def obtener_tiendas() -> pd.DataFrame:
    """
    Devuelve un DataFrame con columnas lat/lon/nombre/direccion listo
    para pintar en el mapa.

    Intenta pedirlas al backend (GET /tiendas). Si el endpoint todavía
    no existe, el backend no está corriendo, o hay cualquier error de
    red, cae de vuelta a los datos de ejemplo para que la vista nunca
    se quede en blanco.
    """
    try:
        resp = requests.get(f"{BACKEND_URL}/tiendas", timeout=3)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return TIENDAS_EJEMPLO

        df = pd.DataFrame(data)
        # Normalizamos nombres de columnas esperados por el mapa
        df = df.rename(columns={"latitud": "lat", "longitud": "lon"})
        return df[["nombre", "direccion", "lat", "lon"]]

    except Exception:
        # Backend caído, endpoint no implementado aún, JSON inesperado, etc.
        return TIENDAS_EJEMPLO


def backend_esta_disponible() -> bool:
    """Chequeo rápido para mostrar un aviso en la interfaz si el backend
    no responde (útil mientras se sigue desarrollando)."""
    try:
        requests.get(f"{BACKEND_URL}/productos", timeout=2)
        return True
    except Exception:
        return False