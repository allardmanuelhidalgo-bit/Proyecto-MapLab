# tests/test_tiendas.py
"""Pruebas de GET/POST /tiendas."""


def test_listar_tiendas_vacio(client):
    r = client.get("/tiendas")
    assert r.status_code == 200
    assert r.json() == []


def test_listar_tiendas_devuelve_las_creadas(client, tienda_cercana, tienda_lejana):
    r = client.get("/tiendas")
    assert r.status_code == 200
    nombres = {t["nombre"] for t in r.json()}
    assert nombres == {"Súper Xtra David", "Super 99 David"}


def test_crear_tienda_ok(client):
    r = client.post("/tiendas", json={
        "nombre": "Minisuper El Ahorro",
        "direccion": "Calle 3, David",
        "latitud": 8.43,
        "longitud": -82.44,
    })
    assert r.status_code == 201
    assert r.json()["nombre"] == "Minisuper El Ahorro"


def test_crear_tienda_nombre_duplicado_da_409(client, tienda_cercana):
    r = client.post("/tiendas", json={
        "nombre": "súper xtra david",  # mismo nombre, otras mayúsculas
        "direccion": "Otra dirección",
        "latitud": 8.0,
        "longitud": -82.0,
    })
    assert r.status_code == 409


def test_crear_tienda_latitud_fuera_de_rango_da_422(client):
    r = client.post("/tiendas", json={
        "nombre": "Tienda Fantasma",
        "latitud": 95.0,  # inválida: fuera de [-90, 90]
        "longitud": -82.0,
    })
    assert r.status_code == 422


def test_crear_tienda_longitud_fuera_de_rango_da_422(client):
    r = client.post("/tiendas", json={
        "nombre": "Tienda Fantasma 2",
        "latitud": 8.0,
        "longitud": 200.0,  # inválida: fuera de [-180, 180]
    })
    assert r.status_code == 422


def test_crear_tienda_en_el_limite_del_rango_es_valida(client):
    """Caso borde: los extremos exactos (90/-180) deben ser válidos, no rechazarse."""
    r = client.post("/tiendas", json={
        "nombre": "Tienda en el Polo",
        "latitud": 90.0,
        "longitud": -180.0,
    })
    assert r.status_code == 201