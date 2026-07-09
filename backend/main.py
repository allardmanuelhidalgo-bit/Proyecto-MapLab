# Archivo base para backend/main.py
from .database import engine, Base
import os

# Esto lee tus modelos de Python y crea automáticamente las 5 tablas en Postgres si no existen
Base.metadata.create_all(bind=engine)