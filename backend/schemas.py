# Archivo base para backend/schemas.py
#
# Estos son los "moldes" que FastAPI usa para convertir los objetos de la base
# de datos (SQLAlchemy) en JSON que el frontend puede consumir, y viceversa.
#
# Convención usada en este archivo:
#   - Los esquemas que terminan en "Out"    -> lo que el API DEVUELVE (lectura)
#   - Los esquemas que terminan en "Create" -> lo que el API RECIBE (creación)

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


# ---------- Categoría ----------

class CategoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


# ---------- Producto ----------

class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    marca: Optional[str] = None
    categoria_id: int


class ProductoCreate(BaseModel):
    nombre: str
    marca: Optional[str] = None
    categoria_id: int


# ---------- Tienda ----------

class TiendaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    direccion: Optional[str] = None
    latitud: float
    longitud: float


class TiendaCreate(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    latitud: float
    longitud: float
    geoapify_id: Optional[str] = None


# ---------- Precio ----------

class PrecioProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    tienda_id: int
    precio: Decimal
    fecha_registro: datetime


class PrecioProductoCreate(BaseModel):
    producto_id: int
    tienda_id: int
    precio: Decimal
    usuario_id: Optional[int] = None


# ---------- Voto ----------
# Un cliente vota si un PrecioProducto (un reporte de precio) es cierto o
# falso. Sin autenticación todavía, así que el usuario_id se manda en el
# body; el día que haya login real, esto se reemplaza por el usuario de la
# sesión y ya no hace falta que el cliente lo declare.

class VotoCreate(BaseModel):
    usuario_id: int
    es_verdadero: bool


class VotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    precio_id: int
    usuario_id: int
    es_verdadero: bool
    fecha_voto: datetime


# ---------- Lista personal de productos ----------

class ItemListaCreate(BaseModel):
    usuario_id: int
    producto_id: int


class ItemListaOut(BaseModel):
    """Trae los datos del producto ya incluidos (nombre, marca) para que el
    frontend no tenga que hacer una segunda consulta por cada item."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    producto_nombre: str
    marca: Optional[str] = None
    comprado: bool
    fecha_agregado: datetime


class ItemListaActualizar(BaseModel):
    comprado: bool


# ---------- Esquemas combinados (para las respuestas de comparación) ----------
# Estos son los que usarán los endpoints de los RF1 y RF2: no representan una
# tabla 1 a 1, sino la forma final del JSON que el frontend necesita mostrar.

class PrecioEnTienda(BaseModel):
    """Precio de UN producto en UNA tienda específica, con la distancia
    al usuario ya calculada. Es la pieza base de la comparación (RF2)."""
    model_config = ConfigDict(from_attributes=True)

    precio_id: int  # id del reporte de precio; el frontend lo necesita para poder votar (POST /precios/{precio_id}/votar)
    tienda_id: int
    tienda_nombre: str
    direccion: Optional[str] = None
    latitud: float
    longitud: float
    precio: Decimal
    fecha_registro: datetime
    votos_a_favor: int = 0
    votos_en_contra: int = 0
    distancia_km: Optional[float] = None  # se calcula en el backend, no viene de la tabla


class ProductoConPrecios(BaseModel):
    """Respuesta principal para 'buscar un producto y comparar precios'
    (RF1 + RF2 juntos): el producto y su precio en cada tienda cercana."""
    model_config = ConfigDict(from_attributes=True)

    producto_id: int
    producto_nombre: str
    marca: Optional[str] = None
    precios: list[PrecioEnTienda]


# ---------- Usuario (opcional, solo si el equipo decide usar login) ----------

class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    fecha_registro: datetime


class UsuarioCreate(BaseModel):
    nombre: str
    email: str

# ---------- Notificación (generada por tareas asíncronas) ----------

class NotificacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    mensaje: str
    producto_id: Optional[int] = None
    tienda_id: Optional[int] = None
    fecha_creacion: datetime