"""
Diagnóstico v2: compara NOMBRE y TIPO de cada columna entre lo que
backend/models.py espera y lo que realmente existe en la base de datos.

El script anterior (diagnostico_columnas.py) solo comparaba nombres. Este
además revisa el tipo, porque un desajuste de tipo (ej. la columna es
NUMERIC en la base pero el modelo espera Float) no rompe la conexión ni
aparece como columna faltante, pero sí puede tronar más adelante cuando
el código intenta usar ese valor (ej. geopy esperando un float y
recibiendo un Decimal).

Uso:
    python diagnostico_tipos.py
"""
from backend.database import DATABASE_URL, engine, Base
from backend import models  # noqa: F401
from sqlalchemy import inspect

if "@" in DATABASE_URL:
    print(f"Conectando a: ***@{DATABASE_URL.split('@')[1]}")
else:
    print(f"Conectando a: {DATABASE_URL}")

inspector = inspect(engine)
tablas_reales = set(inspector.get_table_names())
hay_problemas = False

for nombre_tabla, tabla in Base.metadata.tables.items():
    if nombre_tabla not in tablas_reales:
        print(f"\n❌ La tabla '{nombre_tabla}' no existe en la base de datos.")
        hay_problemas = True
        continue

    columnas_reales = {c["name"]: c["type"] for c in inspector.get_columns(nombre_tabla)}
    avisos_tabla = []

    for columna in tabla.columns:
        if columna.name not in columnas_reales:
            avisos_tabla.append(f"   '{columna.name}': el modelo la espera y NO existe en la DB")
            continue

        tipo_esperado = str(columna.type)
        tipo_real = str(columnas_reales[columna.name])

        # Comparación simple por familia de tipo, no exacta, para no generar
        # falsos positivos por detalles menores (ej. VARCHAR(100) vs VARCHAR)
        familia_esperada = tipo_esperado.split("(")[0].upper()
        familia_real = tipo_real.split("(")[0].upper()

        equivalencias = {
            "FLOAT": {"FLOAT", "REAL", "DOUBLE PRECISION"},
            "DATETIME": {"DATETIME", "TIMESTAMP", "TIMESTAMP WITHOUT TIME ZONE"},
            "BOOLEAN": {"BOOLEAN", "BOOL"},
            "INTEGER": {"INTEGER", "INT", "BIGINT", "SERIAL", "BIGSERIAL"},
        }

        coincide = familia_esperada == familia_real
        if not coincide:
            for _, grupo in equivalencias.items():
                if familia_esperada in grupo and familia_real in grupo:
                    coincide = True
                    break

        if not coincide:
            avisos_tabla.append(
                f"   '{columna.name}': el modelo espera {tipo_esperado}, "
                f"la DB tiene {tipo_real}"
            )

    if avisos_tabla:
        hay_problemas = True
        print(f"\n⚠️  Tabla '{nombre_tabla}':")
        for aviso in avisos_tabla:
            print(aviso)
    else:
        print(f"✅ Tabla '{nombre_tabla}' OK ({len(tabla.columns)} columnas, nombres y tipos coinciden)")

if not hay_problemas:
    print("\nTodo coincide, nombres y tipos. El 500 no es un desajuste de esquema.")
else:
    print("\n--- Encontramos desajustes de TIPO. Esto puede tronar código que asume un tipo específico (ej. float). ---")
