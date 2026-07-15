# tests/conftest.py
#
# IMPORTANTE: esto tiene que ir ANTES de importar nada de "backend".
# backend/database.py lee DATABASE_URL con os.getenv() apenas se importa,
# y backend/main.py corre Base.metadata.create_all(bind=engine) en cuanto
# se importa el módulo. Si no forzamos esta variable primero, los tests
# terminarían creando tablas en tu base de Neon real (o en tu test.db local)
# en lugar de en una base descartable. python-dotenv NO pisa una variable
# que ya exista en el entorno, así que esto es seguro.
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.main import app, get_db
from backend import models

# Motor de pruebas: SQLite en memoria, con StaticPool para que todas las
# conexiones del pool compartan la MISMA base en memoria (si no, cada
# conexión nueva vería una base vacía y "no existe la tabla").
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    """Crea las tablas antes de cada test y las borra al terminar,
    así cada test arranca con una base 100% limpia (aislamiento total)."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """Cliente de pruebas que usa la sesión de arriba en vez de conectarse
    a la base real. No hace falta levantar uvicorn para correr esto."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------
# Fixtures de datos base, para no repetir el mismo setup en cada test.
# Los valores de tiendas/coordenadas son los mismos que usa API_DOCS.md
# como ejemplo, así los tests son fáciles de comparar con la documentación.
# ---------------------------------------------------------------------

@pytest.fixture()
def categoria(db_session):
    cat = models.Categoria(nombre="Lácteos")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


@pytest.fixture()
def producto(db_session, categoria):
    prod = models.Producto(nombre="Leche entera 1L", marca="Estrella Azul", categoria_id=categoria.id)
    db_session.add(prod)
    db_session.commit()
    db_session.refresh(prod)
    return prod


@pytest.fixture()
def tienda_cercana(db_session):
    """Súper Xtra David — más lejos del punto de referencia (ver API_DOCS.md)."""
    t = models.Tienda(
        nombre="Súper Xtra David",
        direccion="Urbanización Brisas Davideñas, David, Chiriquí",
        latitud=8.4286421,
        longitud=-82.4442399,
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


@pytest.fixture()
def tienda_lejana(db_session):
    """Super 99 David — más cerca del punto de referencia (ver API_DOCS.md)."""
    t = models.Tienda(
        nombre="Super 99 David",
        direccion="Calle F Sur, San Mateo, David, Chiriquí",
        latitud=8.4280232,
        longitud=-82.4370701,
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


@pytest.fixture()
def usuario(db_session):
    u = models.Usuario(nombre="Ana Pérez", email="ana@example.com")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture()
def otro_usuario(db_session):
    u = models.Usuario(nombre="Beto Ruiz", email="beto@example.com")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u