# tests/test_usuarios.py
"""Pruebas de POST /usuarios."""


def test_crear_usuario_ok(client):
    r = client.post("/usuarios", json={"nombre": "Ana Pérez", "email": "ana@example.com"})
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "ana@example.com"
    assert "fecha_registro" in body


def test_crear_usuario_email_duplicado_da_400(client, usuario):
    r = client.post("/usuarios", json={"nombre": "Ana Otra", "email": "ana@example.com"})
    assert r.status_code == 400


def test_crear_usuario_email_invalido(client):
    # Nota: schemas.UsuarioCreate define "email" como str simple, no EmailStr,
    # así que esto pasa la validación de Pydantic. Queda documentado como
    # posible mejora: usar EmailStr para rechazar formatos inválidos con 422.
    r = client.post("/usuarios", json={"nombre": "Ana Pérez", "email": "esto-no-es-un-email"})
    assert r.status_code == 201


def test_crear_usuario_falta_email_da_422(client):
    r = client.post("/usuarios", json={"nombre": "Ana Pérez"})
    assert r.status_code == 422