# tests/test_listas.py
"""Pruebas de POST/GET/PATCH/DELETE de /listas."""


def test_agregar_a_lista_ok(client, usuario, producto):
    r = client.post("/listas", json={"usuario_id": usuario.id, "producto_id": producto.id})
    assert r.status_code == 201
    body = r.json()
    assert body["producto_nombre"] == "Leche entera 1L"
    assert body["comprado"] is False


def test_agregar_a_lista_usuario_inexistente_da_404(client, producto):
    r = client.post("/listas", json={"usuario_id": 9999, "producto_id": producto.id})
    assert r.status_code == 404


def test_agregar_a_lista_producto_inexistente_da_404(client, usuario):
    r = client.post("/listas", json={"usuario_id": usuario.id, "producto_id": 9999})
    assert r.status_code == 404


def test_agregar_producto_repetido_a_la_lista_da_409(client, usuario, producto):
    r1 = client.post("/listas", json={"usuario_id": usuario.id, "producto_id": producto.id})
    r2 = client.post("/listas", json={"usuario_id": usuario.id, "producto_id": producto.id})
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_ver_lista_de_usuario_sin_items(client, usuario):
    r = client.get(f"/listas/{usuario.id}")
    assert r.status_code == 200
    assert r.json() == []


def test_ver_lista_usuario_inexistente_da_404(client):
    r = client.get("/listas/9999")
    assert r.status_code == 404


def test_ver_lista_devuelve_items_mas_reciente_primero(client, usuario, db_session):
    from backend_daza import models

    cat = models.Categoria(nombre="Bebidas")
    db_session.add(cat)
    db_session.commit()
    p1 = models.Producto(nombre="Agua", categoria_id=cat.id)
    p2 = models.Producto(nombre="Jugo", categoria_id=cat.id)
    db_session.add_all([p1, p2])
    db_session.commit()

    client.post("/listas", json={"usuario_id": usuario.id, "producto_id": p1.id})
    client.post("/listas", json={"usuario_id": usuario.id, "producto_id": p2.id})

    r = client.get(f"/listas/{usuario.id}")
    nombres = [item["producto_nombre"] for item in r.json()]
    assert nombres == ["Jugo", "Agua"]  # el último agregado va primero


def test_marcar_item_como_comprado(client, usuario, producto):
    item_id = client.post("/listas", json={"usuario_id": usuario.id, "producto_id": producto.id}).json()["id"]
    r = client.patch(f"/listas/{item_id}", json={"comprado": True})
    assert r.status_code == 200
    assert r.json()["comprado"] is True


def test_marcar_item_inexistente_da_404(client):
    r = client.patch("/listas/9999", json={"comprado": True})
    assert r.status_code == 404


def test_quitar_item_de_la_lista(client, usuario, producto):
    item_id = client.post("/listas", json={"usuario_id": usuario.id, "producto_id": producto.id}).json()["id"]
    r = client.delete(f"/listas/{item_id}")
    assert r.status_code == 204

    r_verificar = client.get(f"/listas/{usuario.id}")
    assert r_verificar.json() == []


def test_quitar_item_inexistente_da_404(client):
    r = client.delete("/listas/9999")
    assert r.status_code == 404