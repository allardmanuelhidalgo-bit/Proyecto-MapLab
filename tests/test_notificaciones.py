# tests/test_notificaciones.py
"""Pruebas de las tareas asíncronas (BackgroundTasks) y GET /notificaciones."""

from backend import models


def test_no_hay_notificaciones_al_inicio(client):
    r = client.get("/notificaciones")
    assert r.status_code == 200
    assert r.json() == []


def test_primer_precio_registrado_genera_notificacion_de_precio_minimo(client, producto, tienda_cercana, usuario):
    r = client.post("/precios", json={
        "producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.50, "usuario_id": usuario.id
    })
    assert r.status_code == 201

    r_notif = client.get("/notificaciones")
    notifs = r_notif.json()
    assert len(notifs) == 1
    assert notifs[0]["tipo"] == "precio_minimo"


def test_precio_mas_alto_que_el_minimo_no_genera_notificacion_nueva(client, producto, tienda_cercana, tienda_lejana):
    client.post("/precios", json={"producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.20})
    # Este segundo precio es MÁS ALTO que el anterior, no debería generar notificación.
    client.post("/precios", json={"producto_id": producto.id, "tienda_id": tienda_lejana.id, "precio": 1.80})

    r_notif = client.get("/notificaciones")
    assert len(r_notif.json()) == 1  # sigue habiendo solo UNA (la del primer precio)


def test_tres_votos_en_contra_genera_notificacion_de_reporte_sospechoso(
    client, producto, tienda_cercana, usuario, otro_usuario, db_session
):
    precio_id = client.post("/precios", json={
        "producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.50, "usuario_id": usuario.id
    }).json()["id"]

    votante_2 = models.Usuario(nombre="Carla Núñez", email="carla@example.com")
    votante_3 = models.Usuario(nombre="Diego Solís", email="diego@example.com")
    db_session.add_all([votante_2, votante_3])
    db_session.commit()

    client.post(f"/precios/{precio_id}/votar", json={"usuario_id": otro_usuario.id, "es_verdadero": False})
    client.post(f"/precios/{precio_id}/votar", json={"usuario_id": votante_2.id, "es_verdadero": False})
    client.post(f"/precios/{precio_id}/votar", json={"usuario_id": votante_3.id, "es_verdadero": False})

    r_notif = client.get("/notificaciones")
    tipos = [n["tipo"] for n in r_notif.json()]
    assert "reporte_sospechoso" in tipos


def test_menos_de_tres_votos_en_contra_no_genera_notificacion_de_sospechoso(
    client, producto, tienda_cercana, usuario, otro_usuario
):
    precio_id = client.post("/precios", json={
        "producto_id": producto.id, "tienda_id": tienda_cercana.id, "precio": 1.50, "usuario_id": usuario.id
    }).json()["id"]

    client.post(f"/precios/{precio_id}/votar", json={"usuario_id": otro_usuario.id, "es_verdadero": False})

    r_notif = client.get("/notificaciones")
    tipos = [n["tipo"] for n in r_notif.json()]
    assert "reporte_sospechoso" not in tipos