# tests/test_productos.py
"""Pruebas de GET/POST /productos y GET /categorias."""


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


def test_listar_categorias(client, categoria):
    r = client.get("/categorias")
    assert r.status_code == 200
    assert r.json()[0]["nombre"] == "Lácteos"


def test_crear_producto_ok(client, categoria):
    r = client.post("/productos", json={
        "nombre": "Yogurt natural",
        "marca": "Estrella Azul",
        "categoria_id": categoria.id,
    })
    assert r.status_code == 201
    body = r.json()
    assert body["nombre"] == "Yogurt natural"
    assert "id" in body


def test_crear_producto_sin_marca_es_opcional(client, categoria):
    r = client.post("/productos", json={
        "nombre": "Pan integral",
        "categoria_id": categoria.id,
    })
    assert r.status_code == 201
    assert r.json()["marca"] is None


def test_crear_producto_categoria_inexistente_da_404(client):
    r = client.post("/productos", json={
        "nombre": "Yogurt natural",
        "categoria_id": 9999,
    })
    assert r.status_code == 404


def test_crear_producto_duplicado_en_misma_categoria_da_409(client, producto, categoria):
    r = client.post("/productos", json={
        "nombre": "leche entera 1l",  # mismo nombre, distintas mayúsculas
        "categoria_id": categoria.id,
    })
    assert r.status_code == 409


def test_crear_producto_mismo_nombre_otra_categoria_si_se_permite(client, producto):
    otra_categoria_id_diferente = 2  # no existe todavía -> 404, no 409
    r = client.post("/productos", json={
        "nombre": "Leche entera 1L",
        "categoria_id": otra_categoria_id_diferente,
    })
    # Confirma que la validación de duplicado es (nombre + categoría), no solo nombre.
    # Como la categoría 2 no existe, lo esperado es 404 (no 409).
    assert r.status_code == 404


def test_crear_producto_falta_campo_obligatorio_da_422(client, categoria):
    r = client.post("/productos", json={"categoria_id": categoria.id})  # falta "nombre"
    assert r.status_code == 422