# tests/test_comparar.py
"""Pruebas de GET /productos/comparar — el endpoint principal (RF1 + RF2).

Tu backend no tiene POST /precios, así que los precios de prueba se
insertan directo con SQLAlchemy (db_session), igual que se hace con las
fixtures de producto/tienda en conftest.py.

Usa el mismo punto de referencia y las mismas dos tiendas que API_DOCS.md
(8.4283, -82.4400) para que estos tests sean fáciles de verificar a mano
contra la documentación.
"""
from backend import models

LAT_PRUEBA = 8.4283
LON_PRUEBA = -82.4400


def _crear_precio(db_session, producto, tienda, precio):
    fila = models.PrecioProducto(producto_id=producto.id, tienda_id=tienda.id, precio=precio)
    db_session.add(fila)
    db_session.commit()
    db_session.refresh(fila)
    return fila


def test_comparar_ok_devuelve_las_dos_tiendas_ordenadas_por_cercania(client, db_session, producto, tienda_cercana, tienda_lejana):
    _crear_precio(db_session, producto, tienda_cercana, 1.25)
    _crear_precio(db_session, producto, tienda_lejana, 1.35)

    r = client.get("/productos/comparar", params={"nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    assert r.status_code == 200
    data = r.json()

    assert data["producto_nombre"] == "Leche entera 1L"
    assert len(data["precios"]) == 2

    distancias = [p["distancia_km"] for p in data["precios"]]
    assert distancias == sorted(distancias), "los resultados deben venir ordenados de más cerca a más lejos"

    campos_esperados = {"tienda_id", "tienda_nombre", "direccion", "precio", "distancia_km"}
    assert campos_esperados.issubset(data["precios"][0].keys())


def test_comparar_busqueda_parcial_e_insensible_a_mayusculas(client, db_session, producto, tienda_cercana):
    _crear_precio(db_session, producto, tienda_cercana, 1.25)

    r = client.get("/productos/comparar", params={"nombre": "LECHE", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    assert r.status_code == 200
    assert r.json()["producto_nombre"] == "Leche entera 1L"


def test_comparar_respeta_el_parametro_limite(client, db_session, producto, tienda_cercana, tienda_lejana):
    _crear_precio(db_session, producto, tienda_cercana, 1.25)
    _crear_precio(db_session, producto, tienda_lejana, 1.35)

    r = client.get("/productos/comparar", params={
        "nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA, "limite": 1
    })
    assert r.status_code == 200
    assert len(r.json()["precios"]) == 1


def test_comparar_producto_inexistente_da_404_no_500(client):
    r = client.get("/productos/comparar", params={
        "nombre": "producto_que_no_existe_xyz", "lat": LAT_PRUEBA, "lon": LON_PRUEBA
    })
    assert r.status_code == 404
    assert "detail" in r.json()


def test_comparar_producto_sin_precios_registrados_da_404(client, producto):
    r = client.get("/productos/comparar", params={"nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    assert r.status_code == 404


def test_comparar_faltan_parametros_obligatorios_da_422(client):
    r = client.get("/productos/comparar", params={"nombre": "leche"})  # faltan lat/lon
    assert r.status_code == 422
