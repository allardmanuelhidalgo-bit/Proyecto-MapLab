# Archivo base para backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Numeric
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
    fecha_actualizacion = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    producto = relationship("Producto", back_populates="precios")
    tienda = relationship("Tienda", back_populates="precios")