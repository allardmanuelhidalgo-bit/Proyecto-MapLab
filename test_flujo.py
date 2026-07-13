"""
Prueba automática de extremo a extremo: DB (Neon) -> backend (FastAPI).
No prueba el frontend porque todavía es un stub.

Requisito: el backend debe estar corriendo en otra terminal:
    python -m uvicorn backend.main:app --reload

Uso:
    python test_flujo.py
"""
import requests

API_URL = "http://127.0.0.1:8000"

# Coordenadas de referencia entre las dos tiendas de prueba en David
LAT_PRUEBA = 8.4283
LON_PRUEBA = -82.4400

resultados = []


def check(nombre_prueba, condicion, detalle=""):
    estado = "✅ PASA" if condicion else "❌ FALLA"
    resultados.append(condicion)
    print(f"{estado} - {nombre_prueba}" + (f"  ({detalle})" if detalle and not condicion else ""))


# --- Prueba 0: el servidor responde ---
try:
    r = requests.get(f"{API_URL}/docs", timeout=5)
    check("El backend está corriendo y responde", r.status_code == 200)
except requests.exceptions.ConnectionError:
    print("❌ FALLA - No se pudo conectar al backend en", API_URL)
    print("   ¿Corriste 'python -m uvicorn backend.main:app --reload' en otra terminal?")
    exit(1)

# --- Prueba 1: GET /productos ---
r = requests.get(f"{API_URL}/productos")
check("GET /productos responde 200", r.status_code == 200, f"código {r.status_code}")

productos = r.json() if r.status_code == 200 else []
check("GET /productos devuelve una lista no vacía", isinstance(productos, list) and len(productos) > 0)

# --- Prueba 2: GET /productos/comparar con un producto que sí existe ---
r = requests.get(f"{API_URL}/productos/comparar", params={
    "nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA
})
check("GET /productos/comparar (producto válido) responde 200", r.status_code == 200, f"código {r.status_code}, body: {r.text[:200]}")

if r.status_code == 200:
    data = r.json()
    check("La respuesta tiene 'precios' con al menos 1 tienda", "precios" in data and len(data["precios"]) >= 1)

    if data.get("precios"):
        distancias = [p["distancia_km"] for p in data["precios"]]
        check("Los precios vienen ordenados por cercanía (más cerca primero)", distancias == sorted(distancias))

        primero = data["precios"][0]
        campos_esperados = {"tienda_id", "tienda_nombre", "direccion", "latitud", "longitud", "precio", "distancia_km"}
        check("Cada tienda en 'precios' trae todos los campos esperados", campos_esperados.issubset(primero.keys()))

# --- Prueba 3: GET /productos/comparar con un producto que NO existe ---
r = requests.get(f"{API_URL}/productos/comparar", params={
    "nombre": "producto_que_no_existe_xyz", "lat": LAT_PRUEBA, "lon": LON_PRUEBA
})
check("Buscar un producto inexistente responde 404 (no 500)", r.status_code == 404, f"código {r.status_code}")
check("El error 404 trae un mensaje 'detail' legible", "detail" in r.json() if r.status_code == 404 else False)

# --- Resumen ---
total = len(resultados)
exitosas = sum(resultados)
print(f"\n{exitosas}/{total} pruebas pasaron.")
if exitosas == total:
    print("El flujo DB -> backend está sólido. Listo para conectar el frontend.")
else:
    print("Revisa las pruebas marcadas con ❌ antes de seguir.")