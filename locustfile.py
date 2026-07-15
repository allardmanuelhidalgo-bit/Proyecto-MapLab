"""
Pruebas de carga (RNF de rendimiento/escalabilidad) para la API de MapLab.

Uso:
    1. Levanta el backend:      uvicorn backend.main:app --reload
    2. (una sola vez) Siembra datos de prueba:  python seed.py
    3. Corre Locust:            locust -f locustfile.py --host=http://127.0.0.1:8000
    4. Abre el dashboard:       http://localhost:8089

Los productos y coordenadas usados aquí vienen de tu propio seed.py
(tiendas en David, Chiriquí), así que las búsquedas van a encontrar
resultados reales en vez de dar 404 todo el tiempo.
"""

import random
import uuid

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

# IDs que existen tras correr seed.py (2 tiendas, 7 productos)
TIENDA_IDS = [1, 2]
PRODUCTO_IDS = [1, 2, 3, 4, 5, 6, 7]


class MapLabUser(HttpUser):
    """Simula a un usuario típico: sobre todo consulta y compara precios,
    a veces reporta un precio nuevo o vota, rara vez crea catálogo nuevo."""

    # Espera entre 1 y 3 segundos entre acciones, como un usuario real
    # pensando qué tocar en la app, no un bucle a máxima velocidad.
    wait_time = between(1, 3)

    def on_start(self):
        """Se ejecuta una vez por usuario simulado al arrancar. Guarda un
        precio_id real consultando /productos/comparar, para poder votarlo
        más adelante sin inventar un id que no existe."""
        self.precio_id_conocido = None
        with self.client.get(
            f"/productos/comparar?nombre=Leche&lat={LAT_REF}&lon={LON_REF}",
            name="/productos/comparar [on_start]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                precios = data.get("precios", [])
                if precios:
                    self.precio_id_conocido = precios[0]["precio_id"]

    # --- Lecturas: son las que más carga real reciben en un sitio así ---

    @task(5)
    def comparar_producto(self):
        """El endpoint más pesado: hace búsqueda + cálculo de distancias.
        Es el que más te interesa medir para el RNF de rendimiento."""
        nombre = random.choice(PRODUCTOS)
        self.client.get(
            f"/productos/comparar?nombre={nombre}&lat={LAT_REF}&lon={LON_REF}",
            name="/productos/comparar",
        )

    @task(3)
    def listar_productos(self):
        self.client.get("/productos", name="/productos [GET]")

    @task(2)
    def listar_tiendas(self):
        self.client.get("/tiendas", name="/tiendas [GET]")

    @task(1)
    def listar_categorias(self):
        self.client.get("/categorias", name="/categorias [GET]")

    # --- Escrituras: menos frecuentes, como en un uso real ---

    @task(1)
    def reportar_precio(self):
        """Un usuario reporta el precio que vio en una tienda."""
        payload = {
            "producto_id": random.choice(PRODUCTO_IDS),
            "tienda_id": random.choice(TIENDA_IDS),
            "precio": round(random.uniform(0.5, 6.0), 2),
        }
        self.client.post("/precios", json=payload, name="/precios [POST]")

    @task(1)
    def votar_precio(self):
        """Vota el reporte que guardamos en on_start, si conseguimos uno."""
        if not self.precio_id_conocido:
            return
        payload = {
            # usuario_id fijo de prueba: ajusta si tu seed.py no crea
            # usuarios, o cámbialo por el resultado de crear_usuario()
            "usuario_id": 1,
            "es_verdadero": random.choice([True, False]),
        }
        self.client.post(
            f"/precios/{self.precio_id_conocido}/votar",
            json=payload,
            name="/precios/{id}/votar [POST]",
            # Puede dar 409 (ya votó) o 400 (voto su propio reporte);
            # ambos son respuestas válidas del negocio, no errores del
            # servidor, así que no los contamos como falla.
            catch_response=True,
        ).success()

    @task(1)
    def crear_usuario(self):
        """Registro de usuario nuevo, con email único para no chocar con
        el 400 de email duplicado."""
        email = f"user_{uuid.uuid4().hex[:8]}@ejemplo.com"
        self.client.post(
            "/usuarios",
            json={"nombre": "Usuario de prueba", "email": email},
            name="/usuarios [POST]",
        )