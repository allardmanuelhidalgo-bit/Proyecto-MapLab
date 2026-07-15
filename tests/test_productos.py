# tests/test_productos.py
"""Pruebas de GET /productos.

Tu backend no tiene POST /productos ni GET /categorias, así que este
archivo se recortó a lo único que existe.
"""


def test_listar_productos_vacio(client):
    r = client.get("/productos")
    assert r.status_code == 200
    assert r.json() == []


def test_listar_productos_devuelve_los_creados(client, producto):
    r = client.get("/productos")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Leche entera 1L"
    assert data[0]["marca"] == "Estrella Azul"
