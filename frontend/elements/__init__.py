# frontend/elementos/__init__.py
#
# Este archivo convierte la carpeta "elementos" en un paquete de Python,
# para poder hacer imports como:
#
#   from elementos.header import render_header
#
# Aquí también se pueden "re-exportar" las funciones más usadas para
# poder importarlas de forma más corta, por ejemplo:
#
#   from elementos import render_header
#
# en vez de escribir la ruta completa cada vez.

from elements.header import render_header

__all__ = ["render_header"]
