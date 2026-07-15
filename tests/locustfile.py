"""
Pruebas de carga (RNF de rendimiento/escalabilidad) para la API de MapLab.

Tu backend solo expone GET /productos y GET /productos/comparar, así que
este archivo se recortó a esos dos endpoints (nada de /tiendas, /categorias,
POST /precios, votos ni usuarios: no existen todavía en tu código).

Uso:
    1. Levanta el backend:      python -m uvicorn backend.main:app --reload
    2. (una sola vez) Siembra datos de prueba:  python seed.py
    3. Corre Locust en modo headless (terminal, sin dashboard web):
       locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 20 -r 5 --run-time 60s
"""

import random

from locust import HttpUser, task, between

# --- Datos de referencia tomados de seed.py ---
PRODUCTOS = [
    "Leche entera 1L",
    "Queso blanco 500g",
    "Arroz 1lb",
    "Aceite vegetal 1L",
    "Azúcar blanca 1lb",
    "Detergente líquido 1L",
    "Papel higiénico x4",
]

# Punto de referencia entre las dos tiendas de prueba en David (el mismo
# que usa el ejemplo de API_DOCS.md)
LAT_REF = 8.4283
LON_REF = -82.4400


class MapLabUser(HttpUser):
    """Simula a un usuario típico: sobre todo compara precios, a veces
    solo revisa el catálogo de productos."""

    # Espera entre 1 y 3 segundos entre acciones, como un usuario real
    # pensando qué tocar en la app, no un bucle a máxima velocidad.
    wait_time = between(1, 3)

    @task(5)
    def comparar_producto(self):
        """El endpoint más pesado: hace búsqueda + cálculo de distancias.
        Es el que más te interesa medir para el RNF de rendimiento."""
        nombre = random.choice(PRODUCTOS)
        self.client.get(
            f"/productos/comparar?nombre={nombre}&lat={LAT_REF}&lon={LON_REF}",
            name="/productos/comparar",
        )

    @task(2)
    def listar_productos(self):
        self.client.get("/productos", name="/productos [GET]")
