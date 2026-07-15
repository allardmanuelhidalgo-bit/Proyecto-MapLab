# Archivo base para backend/main.py
import traceback
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from geopy.distance import geodesic
from typing import List

from .database import engine, Base, SessionLocal
from . import models  # necesario: registra las tablas en Base.metadata
from . import schemas

# Crea las tablas si no existen (no borra ni toca las que ya están)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MapLab - Comparador de precios")


# --- SOLO PARA DEBUG LOCAL: muestra el error real en vez de "Internal Server Error" ---
# Imprime la traza completa en la terminal donde corre uvicorn Y la manda en la
# respuesta, para poder verla en el expander del frontend. Quitar antes de producción:
# expone detalles internos (nombres de tablas, rutas de archivos, etc.) a cualquiera.
@app.exception_handler(Exception)
async def manejador_debug(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )


# --- Dependencia: una sesión de DB por request, que se cierra sola al terminar ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoint simple: listar productos (sirve para que el frontend arme un buscador/autocompletar) ---
@app.get("/productos", response_model=List[schemas.ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).all()


# --- Endpoint principal: RF1 + RF2 juntos ---
# Busca un producto por nombre, calcula la distancia del usuario a cada tienda
# que tiene ese producto, y devuelve el precio en las N tiendas más cercanas.
@app.get("/productos/comparar", response_model=schemas.ProductoConPrecios)
def comparar_producto(
    nombre: str = Query(..., description="Nombre (o parte del nombre) del producto a buscar"),
    lat: float = Query(..., description="Latitud del usuario"),
    lon: float = Query(..., description="Longitud del usuario"),
    limite: int = Query(2, description="Cuántas tiendas cercanas devolver"),
    db: Session = Depends(get_db),
):
    # Búsqueda parcial e insensible a mayúsculas: "leche" encuentra "Leche entera 1L"
    producto = (
        db.query(models.Producto)
        .filter(func.lower(models.Producto.nombre).contains(nombre.lower()))
        .first()
    )

    if producto is None:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún producto que coincida con '{nombre}'")

    # Todos los precios registrados de ese producto, cada uno con su tienda
    precios_registrados = (
        db.query(models.PrecioProducto)
        .filter(models.PrecioProducto.producto_id == producto.id)
        .all()
    )

    if not precios_registrados:
        raise HTTPException(status_code=404, detail=f"'{producto.nombre}' no tiene precios registrados en ninguna tienda")

    ubicacion_usuario = (lat, lon)

    # Calculamos distancia real (en km) del usuario a cada tienda con precio de este producto
    precios_con_distancia = []
    for registro in precios_registrados:
        tienda = registro.tienda
        distancia_km = geodesic(
            ubicacion_usuario,
            (tienda.latitud, tienda.longitud)
        ).km

        precios_con_distancia.append(
            schemas.PrecioEnTienda(
                tienda_id=tienda.id,
                tienda_nombre=tienda.nombre,
                direccion=tienda.direccion,
                precio=registro.precio,
                distancia_km=round(distancia_km, 2),
            )
        )

    # Ordenamos por cercanía y nos quedamos solo con las N tiendas más cercanas (RF2)
    precios_con_distancia.sort(key=lambda p: p.distancia_km)
    precios_mas_cercanos = precios_con_distancia[:limite]

    return schemas.ProductoConPrecios(
        producto_id=producto.id,
        producto_nombre=producto.nombre,
        marca=producto.marca,
        precios=precios_mas_cercanos,
    )