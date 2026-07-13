# backend/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carga el archivo .env (no se sube a git, cada quien tiene el suyo)
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")


if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,      # conexiones abiertas en reposo, listas para usar
        max_overflow=20,   # conexiones extra permitidas bajo mucha demanda
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()