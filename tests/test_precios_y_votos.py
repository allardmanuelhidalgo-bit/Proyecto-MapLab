# tests/test_precios_y_votos.py
"""Pruebas de POST /precios y POST /precios/{precio_id}/votar."""


def _registrar_precio(client, producto, tienda, usuario=None, precio=1.35):
    body = {"producto_id": producto.id, "tienda_id": tienda.id, "precio": precio}
    if usuario is not None:
        body["usuario_id"] = usuario.id
    return client.post("/precios", json=body)


# ---------- POST /precios ----------

def test_registrar_precio_ok(client, producto, tienda_cercana, usuario):
    r = _registrar_precio(client, producto, tienda_cercana, usuario)
    assert r.status_code == 201
    body = r.json()
    assert float(body["precio"]) == 1.35
    assert "fecha_registro" in body


def test_registrar_precio_sin_usuario_es_opcional(client, producto, tienda_cercana):
    r = _registrar_precio(client, producto, tienda_cercana, usuario=None)
    assert r.status_code == 201


def test_registrar_precio_dos_veces_crea_dos_reportes(client, producto, tienda_cercana, usuario):
    """Cada POST /precios crea un reporte NUEVO, no sobreescribe el anterior."""
    r1 = _registrar_precio(client, producto, tienda_cercana, usuario, precio=1.35)
    r2 = _registrar_precio(client, producto, tienda_cercana, usuario, precio=1.30)
    assert r1.status_code == 201 and r2.status_code == 201
    assert r1.json()["id"] != r2.json()["id"]


def test_registrar_precio_producto_inexistente_da_404(client, tienda_cercana):
    r = client.post("/precios", json={"producto_id": 9999, "tienda_id": tienda_cercana.id, "precio": 1.0})
    assert r.status_code == 404


def test_registrar_precio_tienda_inexistente_da_404(client, producto):
    r = client.post("/precios", json={"producto_id": producto.id, "tienda_id": 9999, "precio": 1.0})
    assert r.status_code == 404


def test_registrar_precio_usuario_inexistente_da_404(client, producto, tienda_cercana):
    r = client.post("/precios", json={
        "producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.0, "usuario_id": 9999
    })
    assert r.status_code == 404


def test_registrar_precio_negativo_o_cero_da_422(client, producto, tienda_cercana):
    r_negativo = _registrar_precio(client, producto, tienda_cercana, precio=-5)
    r_cero = _registrar_precio(client, producto, tienda_cercana, precio=0)
    assert r_negativo.status_code == 422
    assert r_cero.status_code == 422


# ---------- POST /precios/{precio_id}/votar ----------

def test_votar_ok(client, producto, tienda_cercana, usuario, otro_usuario):
    precio_id = _registrar_precio(client, producto, tienda_cercana, usuario).json()["id"]
    r = client.post(f"/precios/{precio_id}/votar", json={"usuario_id": otro_usuario.id, "es_verdadero": True})
    assert r.status_code == 201
    assert r.json()["es_verdadero"] is True


def test_votar_precio_inexistente_da_404(client, usuario):
    r = client.post("/precios/9999/votar", json={"usuario_id": usuario.id, "es_verdadero": True})
    assert r.status_code == 404


def test_votar_usuario_inexistente_da_404(client, producto, tienda_cercana, usuario):
    precio_id = _registrar_precio(client, producto, tienda_cercana, usuario).json()["id"]
    r = client.post(f"/precios/{precio_id}/votar", json={"usuario_id": 9999, "es_verdadero": True})
    assert r.status_code == 404


def test_votar_el_propio_reporte_da_400(client, producto, tienda_cercana, usuario):
    precio_id = _registrar_precio(client, producto, tienda_cercana, usuario).json()["id"]
    r = client.post(f"/precios/{precio_id}/votar", json={"usuario_id": usuario.id, "es_verdadero": True})
    assert r.status_code == 400


def test_votar_dos_veces_el_mismo_reporte_da_409(client, producto, tienda_cercana, usuario, otro_usuario):
    precio_id = _registrar_precio(client, producto, tienda_cercana, usuario).json()["id"]
    r1 = client.post(f"/precios/{precio_id}/votar", json={"usuario_id": otro_usuario.id, "es_verdadero": True})
    r2 = client.post(f"/precios/{precio_id}/votar", json={"usuario_id": otro_usuario.id, "es_verdadero": False})
    assert r1.status_code == 201
    assert r2.status_code == 409