# tests/test_comparar.py
"""Pruebas de GET /productos/comparar — el endpoint principal (RF1 + RF2).

Usa el mismo punto de referencia y las mismas dos tiendas que API_DOCS.md
(8.4283, -82.4400) para que estos tests sean fáciles de verificar a mano
contra la documentación.
"""

LAT_PRUEBA = 8.4283
LON_PRUEBA = -82.4400


def _con_precios_en_ambas_tiendas(client, producto, tienda_cercana, tienda_lejana):
    client.post("/precios", json={"producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.25})
    client.post("/precios", json={"producto_id": producto.id, "tienda_id": tienda_lejana.id, "precio": 1.35})


def test_comparar_ok_devuelve_las_dos_tiendas_ordenadas_por_cercania(client, producto, tienda_cercana, tienda_lejana):
    _con_precios_en_ambas_tiendas(client, producto, tienda_cercana, tienda_lejana)

    r = client.get("/productos/comparar", params={"nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    assert r.status_code == 200
    data = r.json()

    assert data["producto_nombre"] == "Leche entera 1L"
    assert len(data["precios"]) == 2

    distancias = [p["distancia_km"] for p in data["precios"]]
    assert distancias == sorted(distancias), "los resultados deben venir ordenados de más cerca a más lejos"

    campos_esperados = {"precio_id", "tienda_id", "tienda_nombre", "direccion", "precio", "distancia_km"}
    assert campos_esperados.issubset(data["precios"][0].keys())


def test_comparar_busqueda_parcial_e_insensible_a_mayusculas(client, producto, tienda_cercana):
    client.post("/precios", json={"producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.25})

    r = client.get("/productos/comparar", params={"nombre": "LECHE", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    assert r.status_code == 200
    assert r.json()["producto_nombre"] == "Leche entera 1L"


def test_comparar_respeta_el_parametro_limite(client, producto, tienda_cercana, tienda_lejana):
    _con_precios_en_ambas_tiendas(client, producto, tienda_cercana, tienda_lejana)

    r = client.get("/productos/comparar", params={
        "nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA, "limite": 1
    })
    assert r.status_code == 200
    assert len(r.json()["precios"]) == 1


def test_comparar_solo_muestra_el_precio_mas_reciente_por_tienda(client, producto, tienda_cercana):
    """Si una tienda tiene varios reportes del mismo producto, solo debe
    aparecer el más reciente (según fecha_registro), no todos."""
    client.post("/precios", json={"producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.50})
    client.post("/precios", json={"producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.30})

    r = client.get("/productos/comparar", params={"nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    assert r.status_code == 200
    precios = r.json()["precios"]
    assert len(precios) == 1  # una sola tienda -> un solo resultado, no dos


def test_comparar_producto_inexistente_da_404_no_500(client):
    r = client.get("/productos/comparar", params={
        "nombre": "producto_que_no_existe_xyz", "lat": LAT_PRUEBA, "lon": LON_PRUEBA
    })
    assert r.status_code == 404
    assert "detail" in r.json()


def test_comparar_producto_sin_precios_registrados_da_404(client, producto):
    r = client.get("/productos/comparar", params={"nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    assert r.status_code == 404


def test_comparar_incluye_conteo_de_votos(client, producto, tienda_cercana, usuario, otro_usuario):
    precio_id = client.post("/precios", json={
        "producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.25, "usuario_id": usuario.id
    }).json()["id"]
    client.post(f"/precios/{precio_id}/votar", json={"usuario_id": otro_usuario.id, "es_verdadero": True})

    r = client.get("/productos/comparar", params={"nombre": "leche", "lat": LAT_PRUEBA, "lon": LON_PRUEBA})
    resultado = r.json()["precios"][0]
    assert resultado["votos_a_favor"] == 1
    assert resultado["votos_en_contra"] == 0


def test_comparar_faltan_parametros_obligatorios_da_422(client):
    r = client.get("/productos/comparar", params={"nombre": "leche"})  # faltan lat/lon
    assert r.status_code == 422