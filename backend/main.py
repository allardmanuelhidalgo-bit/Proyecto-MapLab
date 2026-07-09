# Archivo base para backend/main.py
from .database import engine, Base
import os

# Esto lee tus modelos de Python y crea automáticamente las 5 tablas en Postgres si no existen
Base.metadata.create_all(bind=engine)
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import math

from .database import engine, Base, get_db
from . import models, schemas

# Crear las tablas en PostgreSQL al arrancar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Comparador Inteligente de Precios")

# --- FUNCIÓN AUXILIAR: HERSINE FORMULA ---
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia en kilómetros entre dos coordenadas geográficas."""
    R = 6371.0 # Radio de la Tierra en km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

# --- ENDPOINTS ---

@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.post("/stores/", response_model=schemas.StoreResponse)
def create_store(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    db_store = models.Store(**store.model_dump())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@app.post("/prices/")
def register_price(price_data: schemas.PriceCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe un precio para ese producto en esa tienda
    existing = db.query(models.StoreProduct).filter(
        models.StoreProduct.store_id == price_data.store_id,
        models.StoreProduct.product_id == price_data.product_id
    ).first()

    if existing:
        existing.price = price_data.price
        db.commit()
        return {"message": "Precio actualizado exitosamente"}
    
    db_price = models.StoreProduct(**price_data.model_dump())
    db.add(db_price)
    db.commit()
    return {"message": "Precio registrado exitosamente"}

@app.get("/compare/", response_model=List[schemas.ComparisonResult])
def compare_prices(
    product_id: int, 
    lat: float, 
    lon: float, 
    sort_by: str = Query("price", description="Ordenar por 'price' o 'distance'"),
    db: Session = Depends(get_db)
):
    # Obtener todas las tiendas que tienen el producto registrado
    results = db.query(models.StoreProduct).filter(models.StoreProduct.product_id == product_id).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="Producto no encontrado o sin precios registrados.")

    comparison_list = []
    
    for item in results:
        distance = calculate_distance(lat, lon, item.store.latitude, item.store.longitude)
        
        comparison_list.append({
            "product_name": item.product.name,
            "brand": item.product.brand,
            "store_name": item.store.name,
            "price": item.price,
            "distance_km": round(distance, 2),
            "updated_at": item.updated_at
        })
    
    # Lógica de ordenamiento solicitada
    if sort_by == "distance":
        comparison_list.sort(key=lambda x: x["distance_km"])
    else:
        comparison_list.sort(key=lambda x: x["price"])
        
    return comparison_list