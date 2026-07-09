# Archivo base para backend/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Esquemas para Producto
class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True

# Esquemas para Tienda
class StoreBase(BaseModel):
    name: str
    address: Optional[str] = None
    latitude: float
    longitude: float

class StoreCreate(StoreBase):
    pass

class StoreResponse(StoreBase):
    id: int
    class Config:
        from_attributes = True

# Esquema para Registrar Precio Manual
class PriceCreate(BaseModel):
    store_id: int
    product_id: int
    price: float

# Esquema para la Respuesta de la Comparación
class ComparisonResult(BaseModel):
    product_name: str
    brand: Optional[str]
    store_name: str
    price: float
    distance_km: float
    updated_at: datetime