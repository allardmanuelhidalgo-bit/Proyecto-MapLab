"""
Diagnóstico rápido: confirma qué conexión se está usando y si de verdad
llega a Neon. Correr con: python check_db.py
"""
from backend.database import DATABASE_URL, engine, Base
from backend import models  # necesario para que Base.metadata conozca las tablas
from sqlalchemy import inspect, text

# 1. Mostrar qué URL se está usando realmente (ocultando la contraseña)
if "@" in DATABASE_URL:
    partes = DATABASE_URL.split("@")
    print(f"DATABASE_URL detectada: ***@{partes[1]}")
else:
    print(f"DATABASE_URL detectada: {DATABASE_URL}")

if "localhost" in DATABASE_URL:
    print("\n⚠️  ADVERTENCIA: está usando localhost, no Neon.")
    print("   Esto significa que el archivo .env NO se está leyendo.")
    print("   Revisa que .env esté en la raíz del proyecto y sin BOM.\n")

# 2. Intentar conectar de verdad
try:
    with engine.connect() as conn:
        resultado = conn.execute(text("SELECT current_database();"))
        print(f"Conexión exitosa. Base de datos actual: {resultado.scalar()}")
except Exception as e:
    print(f"\n❌ No se pudo conectar: {e}")
    exit()

# 3. Crear tablas y luego listar qué existe
Base.metadata.create_all(bind=engine)
inspector = inspect(engine)
tablas = inspector.get_table_names()
print(f"\nTablas encontradas en esta base: {tablas}")