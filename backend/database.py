# Archivo base para backend/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carga el archivo .env (no se sube a git, cada quien tiene el suyo)
load_dotenv()

# Formato: postgresql://usuario:contraseña@servidor:puerto/nombre_base_datos
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/comparador_db"
)

# Creamos el motor de base de datos específico para PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_size=10,         # Mantiene un grupo de 10 conexiones abiertas para máxima velocidad
    max_overflow=20       # Permite abrir hasta 20 conexiones extras bajo mucha demanda
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Esta función la usará FastAPI para abrir y cerrar la conexión en cada clic del usuario
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()