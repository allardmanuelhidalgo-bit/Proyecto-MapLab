"""
Diagnóstico: compara las columnas que backend/models.py ESPERA contra las
columnas que realmente existen en la base de datos a la que te conectas.

Por qué esto puede pasar: Base.metadata.create_all() SOLO crea tablas que
no existen. Si una tabla ya existía en tu base de Neon y luego alguien
agregó una columna nueva al modelo (ej. "geoapify_id"), create_all() NO
la agrega a la tabla existente — necesitarías una migración (Alembic) o
borrar y recrear la tabla. Este script te dice exactamente qué falta.

Uso:
    python diagnostico_columnas.py
"""
from backend_daza.database import DATABASE_URL, engine, Base
from backend_daza import models  # noqa: F401 (necesario para poblar Base.metadata)
from sqlalchemy import inspect

if "@" in DATABASE_URL:
    print(f"Conectando a: ***@{DATABASE_URL.split('@')[1]}")
else:
    print(f"Conectando a: {DATABASE_URL}")

inspector = inspect(engine)
tablas_reales = set(inspector.get_table_names())

hay_problemas = False

for nombre_tabla, tabla in Base.metadata.tables.items():
    columnas_esperadas = {c.name for c in tabla.columns}

    if nombre_tabla not in tablas_reales:
        print(f"\n❌ La tabla '{nombre_tabla}' NO EXISTE en la base de datos.")
        hay_problemas = True
        continue

    columnas_reales = {c["name"] for c in inspector.get_columns(nombre_tabla)}
    faltantes = columnas_esperadas - columnas_reales
    sobrantes = columnas_reales - columnas_esperadas

    if faltantes or sobrantes:
        hay_problemas = True
        print(f"\n⚠️  Tabla '{nombre_tabla}' no coincide:")
        if faltantes:
            print(f"   Columnas que el modelo espera y NO existen en la DB: {faltantes}")
        if sobrantes:
            print(f"   Columnas que existen en la DB pero ya no están en el modelo: {sobrantes}")
    else:
        print(f"✅ Tabla '{nombre_tabla}' OK ({len(columnas_reales)} columnas, todas coinciden)")

if not hay_problemas:
    print("\nTodo coincide. El problema no es de esquema desincronizado.")
else:
    print("\n--- Encontramos desajustes. Ver 'diagnostico_columnas.py' explica por qué pasa. ---")
