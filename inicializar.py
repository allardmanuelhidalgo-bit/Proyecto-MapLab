import os

# Definimos las carpetas y los archivos base que necesitamos
estructura = {
    "backend": ["__init__.py", "main.py", "database.py", "models.py", "schemas.py"],
    "frontend": ["__init__.py", "app.py", "utils.py"]
}
archivos_raiz = ["requirements.txt", "run.py", "README.md"]

# Ciclo para crear todo en 1 segundo
for carpeta, archivos in estructura.items():
    os.makedirs(carpeta, exist_ok=True)
    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)
        if not os.path.exists(ruta):
            with open(ruta, "w") as f:
                f.write(f"# Archivo base para {carpeta}/{archivo}\n")
            print(f"Creado: {ruta}")

for archivo in archivos_raiz:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            f.write("")
        print(f"Creado en raíz: {archivo}")

print("\n¡Estructura de carpetas lista para trabajar!")