# Archivo base para backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Numeric, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(150), index=True, nullable=False)
    marca = Column(String(100))
    
    precios = relationship("PrecioProducto", back_populates="producto")

class Tienda(Base):
    __tablename__ = "tiendas"
    id = Column(Integer, primary_key=True, index=True)
    geoapify_id = Column(String(200), unique=True, index=True, nullable=True) # ID de la API externa
    nombre = Column(String(150), nullable=False)
    direccion = Column(String(250))
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)

    precios = relationship("PrecioProducto", back_populates="tienda")

class PrecioProducto(Base):
    __tablename__ = "precios_productos"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    tienda_id = Column(Integer, ForeignKey("tiendas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # Numeric(10,2) guarda números exactos como 1250.50 sin perder precisión decimal
    precio = Column(Numeric(10, 2), nullable=False) 

    # Cada reporte de precio es un registro histórico independiente (no se
    # edita in-place): si alguien reporta un precio nuevo para el mismo
    # producto/tienda, se crea una fila nueva. Por eso fecha_registro NO
    # lleva onupdate: es la fecha real en que ese reporte se creó, y nunca
    # cambia después (es lo que pide el RF de "saber cuándo se registró").
    #
    # NOTA: la columna física en la base de datos (Neon) se llama
    # "fecha_actualizacion" por un cambio de nombre que no se migró. En vez
    # de tocar la base de datos, mapeamos el atributo de Python
    # "fecha_registro" (el nombre que usan main.py, schemas.py y los tests)
    # a esa columna real con el primer argumento posicional de Column().
    fecha_registro = Column("fecha_actualizacion", DateTime, default=datetime.datetime.utcnow, nullable=False)

    producto = relationship("Producto", back_populates="precios")
    tienda = relationship("Tienda", back_populates="precios")
    votos = relationship("Voto", back_populates="precio", cascade="all, delete-orphan")


class Voto(Base):
    """Un cliente vota 1 vez (cierto/falso) sobre un reporte de precio
    específico. La UniqueConstraint es lo que impide, a nivel de base de
    datos, que el mismo usuario vote dos veces el mismo precio (no basta con
    validarlo en el endpoint: sin esto, dos requests casi simultáneos podrían
    colarse los dos)."""
    __tablename__ = "votos"
    id = Column(Integer, primary_key=True, index=True)
    precio_id = Column(Integer, ForeignKey("precios_productos.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    es_verdadero = Column(Boolean, nullable=False)
    fecha_voto = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("precio_id", "usuario_id", name="uq_voto_unico_por_usuario"),
    )

    precio = relationship("PrecioProducto", back_populates="votos")
    usuario = relationship("Usuario")


class ItemLista(Base):
    """Un producto que un usuario agregó a su lista personal de compras.
    'comprado' es lo que le permite al usuario ir tachando lo que ya
    consiguió sin borrar el producto de la lista."""
    __tablename__ = "items_lista"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    comprado = Column(Boolean, default=False, nullable=False)
    fecha_agregado = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        # Evita meter el mismo producto dos veces a la lista del mismo usuario
        UniqueConstraint("usuario_id", "producto_id", name="uq_producto_unico_por_lista"),
    )

    usuario = relationship("Usuario")
    producto = relationship("Producto")

class Notificacion(Base):
    """Notificación generada por una tarea en segundo plano (BackgroundTasks).
    No bloquea la respuesta del endpoint que la generó: se crea DESPUÉS
    de que el cliente ya recibió su respuesta HTTP."""
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)  # ej: "precio_minimo", "reporte_sospechoso"
    mensaje = Column(String(300), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=True)
    tienda_id = Column(Integer, ForeignKey("tiendas.id", ondelete="CASCADE"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)